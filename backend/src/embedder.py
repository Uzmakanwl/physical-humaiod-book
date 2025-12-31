"""
Embedding generator module for the embedding pipeline.

This module handles generation of semantic embeddings using Cohere API
and provides quality validation for the generated embeddings.
"""

import cohere
from typing import List, Dict, Any, Optional
import numpy as np
from config import Config
from src.logger import get_logger


class EmbeddingGenerator:
    """Generates semantic embeddings for text content using Cohere API."""

    def __init__(self, model: str = "embed-multilingual-v3.0"):
        """
        Initialize the EmbeddingGenerator.

        Args:
            model: The embedding model to use
        """
        self.model = model
        self.logger = get_logger(__name__)

        # Initialize Cohere client
        if not Config.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(Config.COHERE_API_KEY)

    def generate_embeddings(self, texts: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to generate embeddings for
            batch_size: Batch size for API calls (defaults to config value)

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if not texts:
            return []

        # Use config batch size if not provided
        batch_size = batch_size or Config.BATCH_SIZE

        all_embeddings = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1} of {(len(texts)-1)//batch_size + 1}")

            try:
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document"
                )

                batch_embeddings = [embedding for embedding in response.embeddings]
                all_embeddings.extend(batch_embeddings)

            except Exception as e:
                self.logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Retry with smaller batch size
                if len(batch) > 1:
                    mid = len(batch) // 2
                    left_batch = self.generate_embeddings(batch[:mid], batch_size=max(1, batch_size//2))
                    right_batch = self.generate_embeddings(batch[mid:], batch_size=max(1, batch_size//2))
                    all_embeddings.extend(left_batch)
                    all_embeddings.extend(right_batch)
                else:
                    # If single item fails, append zeros as fallback
                    # In practice, you might want to raise an exception here
                    embedding_dim = 1024  # Default dimension for Cohere embeddings
                    all_embeddings.append([0.0] * embedding_dim)
                    self.logger.warning(f"Using zero embedding for failed text: {batch[0][:50]}...")

        return all_embeddings

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding for a text.

        Args:
            text: Text to generate embedding for

        Returns:
            Embedding as a list of floats
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    def validate_embedding_quality(self, embedding: List[float], text: str) -> Dict[str, Any]:
        """
        Validate the quality of a generated embedding.

        Args:
            embedding: The embedding to validate
            text: The original text that generated the embedding

        Returns:
            Dictionary with validation results
        """
        if not embedding:
            return {
                'is_valid': False,
                'quality_score': 0.0,
                'issues': ['Empty embedding']
            }

        # Check for zero vectors (indicating potential failure)
        if all(val == 0.0 for val in embedding):
            return {
                'is_valid': False,
                'quality_score': 0.0,
                'issues': ['Zero vector - embedding generation may have failed']
            }

        # Check embedding dimension consistency
        expected_dim = len(embedding)
        if expected_dim < 10:  # Very small dimension might indicate an issue
            return {
                'is_valid': False,
                'quality_score': 0.0,
                'issues': [f'Very small embedding dimension: {expected_dim}']
            }

        # Calculate quality metrics
        magnitude = np.linalg.norm(embedding)
        avg_value = np.mean(np.abs(embedding))
        std_value = np.std(embedding)

        # Basic quality assessment
        quality_score = 1.0

        if magnitude < 0.1:
            quality_score -= 0.3
        if avg_value < 0.001:
            quality_score -= 0.2
        if std_value < 0.001:  # Very low variance might indicate poor quality
            quality_score -= 0.1

        quality_score = max(0.0, min(1.0, quality_score))

        issues = []
        if quality_score < 0.5:
            issues.append(f'Low quality embedding (score: {quality_score})')

        return {
            'is_valid': quality_score > 0.3,
            'quality_score': quality_score,
            'issues': issues,
            'metrics': {
                'magnitude': float(magnitude),
                'avg_abs_value': float(avg_value),
                'std_deviation': float(std_value),
                'dimension': len(embedding)
            }
        }

    def check_embedding_consistency(self, embeddings: List[List[float]],
                                  threshold: float = 0.95) -> Dict[str, Any]:
        """
        Check consistency among a set of embeddings.

        Args:
            embeddings: List of embeddings to check for consistency
            threshold: Similarity threshold for consistency check

        Returns:
            Dictionary with consistency check results
        """
        if len(embeddings) < 2:
            return {
                'is_consistent': True,
                'consistency_score': 1.0,
                'issues': []
            }

        # Calculate pairwise similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = self.calculate_similarity(embeddings[i], embeddings[j])
                similarities.append(similarity)

        if not similarities:
            return {
                'is_consistent': True,
                'consistency_score': 1.0,
                'issues': []
            }

        # Calculate average similarity and consistency metrics
        avg_similarity = sum(similarities) / len(similarities)
        max_similarity = max(similarities)
        min_similarity = min(similarities)

        # Determine consistency
        is_consistent = avg_similarity >= threshold
        consistency_score = avg_similarity

        issues = []
        if not is_consistent:
            issues.append(f"Average similarity ({avg_similarity:.3f}) below threshold ({threshold})")
        if max_similarity - min_similarity > 0.5:
            issues.append(f"High variance in similarities (range: {min_similarity:.3f} to {max_similarity:.3f})")

        return {
            'is_consistent': is_consistent,
            'consistency_score': consistency_score,
            'avg_similarity': avg_similarity,
            'min_similarity': min_similarity,
            'max_similarity': max_similarity,
            'issues': issues
        }

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity value between 0 and 1
        """
        if not embedding1 or not embedding2 or len(embedding1) != len(embedding2):
            return 0.0

        v1 = np.array(embedding1)
        v2 = np.array(embedding2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        similarity = dot_product / (norm_v1 * norm_v2)
        # Ensure similarity is between 0 and 1
        return max(0.0, min(1.0, float(similarity)))

    def batch_process_with_validation(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process texts in batch and validate the generated embeddings.

        Args:
            texts: List of texts to process

        Returns:
            List of dictionaries containing text, embedding, and validation results
        """
        embeddings = self.generate_embeddings(texts)
        results = []

        for text, embedding in zip(texts, embeddings):
            validation = self.validate_embedding_quality(embedding, text)
            results.append({
                'text': text,
                'embedding': embedding,
                'validation': validation
            })

        return results