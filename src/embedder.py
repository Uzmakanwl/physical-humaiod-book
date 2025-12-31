"""
Embedding generator module for Cohere integration.

This module provides functionality to generate semantic embeddings for content
using Cohere's embedding API, with support for batch processing and quality validation.
"""
import cohere
from typing import List, Dict, Optional, Tuple
import time
import logging
from dataclasses import dataclass

from src.models.models import EmbeddingResult


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    api_key: str
    model: str = "embed-english-v3.0"  # Default Cohere embedding model
    batch_size: int = 96  # Cohere's recommended batch size
    max_retries: int = 3
    timeout: int = 60
    input_type: str = "search_document"  # Default input type for documents
    truncate: str = "END"  # How to handle text longer than max length


class EmbeddingGenerator:
    """Embedding generator for Cohere integration."""

    def __init__(self, config: EmbeddingConfig):
        """
        Initialize the embedding generator.

        Args:
            config: Embedding configuration
        """
        self.config = config
        self.client = cohere.Client(
            api_key=config.api_key,
            timeout=config.timeout
        )
        self.logger = logging.getLogger(__name__)

    def generate_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of EmbeddingResult objects
        """
        if not texts:
            return []

        all_results = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            batch_results = self._generate_batch_embeddings(batch)
            all_results.extend(batch_results)

        return all_results

    def _generate_batch_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed (up to batch size)

        Returns:
            List of EmbeddingResult objects
        """
        results = []
        start_time = time.time()

        try:
            # Generate embeddings using Cohere API
            response = self.client.embed(
                texts=texts,
                model=self.config.model,
                input_type=self.config.input_type,
                truncate=self.config.truncate
            )

            # Create EmbeddingResult objects for each text
            for i, (text, embedding) in enumerate(zip(texts, response.embeddings)):
                quality_score = self._evaluate_embedding_quality(embedding)
                result = EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    quality_score=quality_score,
                    is_valid=True,
                    generation_time=time.time() - start_time,
                    model_used=self.config.model
                )
                results.append(result)

        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            # Return invalid results for all texts in the batch
            for text in texts:
                result = EmbeddingResult(
                    text=text,
                    embedding=[],
                    quality_score=0.0,
                    is_valid=False,
                    generation_time=time.time() - start_time,
                    model_used=self.config.model
                )
                results.append(result)

        return results

    def _evaluate_embedding_quality(self, embedding: List[float]) -> float:
        """
        Evaluate the quality of an embedding based on various metrics.

        Args:
            embedding: The embedding vector

        Returns:
            Quality score between 0.0 and 1.0
        """
        if not embedding:
            return 0.0

        # Calculate various quality metrics
        magnitude = sum(x ** 2 for x in embedding) ** 0.5
        zero_count = sum(1 for x in embedding if abs(x) < 1e-10)
        variance = self._calculate_variance(embedding)

        # Normalize metrics to 0-1 scale
        magnitude_score = min(1.0, magnitude / 10.0)  # Assuming reasonable magnitude is around 10
        zero_ratio_score = 1.0 - (zero_count / len(embedding))  # Higher is better
        variance_score = min(1.0, variance * 100)  # Higher variance is generally better

        # Weighted average of quality metrics
        quality_score = (
            magnitude_score * 0.3 +
            zero_ratio_score * 0.4 +
            variance_score * 0.3
        )

        return quality_score

    def _calculate_variance(self, values: List[float]) -> float:
        """
        Calculate the variance of a list of values.

        Args:
            values: List of numerical values

        Returns:
            Variance of the values
        """
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def validate_embedding_consistency(self, embeddings: List[EmbeddingResult]) -> bool:
        """
        Validate that embeddings are consistent in terms of quality and dimensions.

        Args:
            embeddings: List of embedding results to validate

        Returns:
            True if consistent, False otherwise
        """
        if not embeddings:
            return True

        # Check if all embeddings have the same dimension
        dimensions = [len(e.embedding) for e in embeddings if e.is_valid]
        if len(set(dimensions)) > 1:
            self.logger.warning("Embeddings have inconsistent dimensions")
            return False

        # Check if quality scores are reasonable
        valid_embeddings = [e for e in embeddings if e.is_valid]
        if not valid_embeddings:
            return False

        avg_quality = sum(e.quality_score for e in valid_embeddings) / len(valid_embeddings)
        if avg_quality < 0.3:  # Threshold for minimum acceptable quality
            self.logger.warning(f"Average embedding quality is low: {avg_quality}")
            return False

        return True

    def generate_embedding_for_text(self, text: str) -> EmbeddingResult:
        """
        Generate a single embedding for a text.

        Args:
            text: Text to embed

        Returns:
            Single EmbeddingResult object
        """
        results = self.generate_embeddings([text])
        return results[0] if results else EmbeddingResult(
            text=text,
            embedding=[],
            quality_score=0.0,
            is_valid=False,
            generation_time=0.0,
            model_used=self.config.model
        )

    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the embedding model being used.

        Returns:
            Dictionary with model information
        """
        # Note: Cohere API doesn't have a direct method to get model info
        # This is based on known information about the default model
        return {
            'model_name': self.config.model,
            'dimensions': 1024,  # embed-english-v3.0 has 1024 dimensions
            'language': 'english',
            'input_type': self.config.input_type,
            'max_batch_size': self.config.batch_size
        }