"""
Vector storage module for Qdrant operations.

This module provides functionality to store embeddings in Qdrant vector database,
perform similarity searches, and manage vector storage operations with proper
metadata linking to source URLs.
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional, Any
import uuid
import time
import logging
from dataclasses import dataclass

from src.models.models import StorageResult, SearchResult


@dataclass
class VectorStorageConfig:
    """Configuration for vector storage operations."""
    host: str = "localhost"
    port: int = 6333
    api_key: Optional[str] = None
    url: Optional[str] = None  # Alternative to host/port for cloud instances
    collection_name: str = "embeddings"
    vector_size: int = 1024  # Default size for Cohere embeddings
    distance: str = "Cosine"  # Cosine similarity
    timeout: int = 60
    max_retries: int = 3


class VectorStorage:
    """Vector storage for Qdrant operations."""

    def __init__(self, config: VectorStorageConfig):
        """
        Initialize the vector storage.

        Args:
            config: Vector storage configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize Qdrant client
        if config.url:
            self.client = QdrantClient(
                url=config.url,
                api_key=config.api_key,
                timeout=config.timeout
            )
        else:
            self.client = QdrantClient(
                host=config.host,
                port=config.port,
                api_key=config.api_key,
                timeout=config.timeout
            )

        # Ensure collection exists
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't."""
        try:
            # Try to get collection info
            self.client.get_collection(self.config.collection_name)
            self.logger.info(f"Collection {self.config.collection_name} already exists")
        except:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=models.VectorParams(
                    size=self.config.vector_size,
                    distance=models.Distance[self.config.distance.upper()]
                )
            )
            self.logger.info(f"Created collection {self.config.collection_name}")

    def store_embeddings(self, texts: List[str], embeddings: List[List[float]],
                        metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[StorageResult]:
        """
        Store embeddings in the vector database.

        Args:
            texts: Original text chunks
            embeddings: Corresponding embeddings
            metadata_list: Optional list of metadata dictionaries

        Returns:
            List of StorageResult objects
        """
        if not texts or not embeddings or len(texts) != len(embeddings):
            raise ValueError("Texts and embeddings must be non-empty and of equal length")

        # Prepare points for Qdrant
        points = []
        results = []

        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            # Generate unique ID for each point
            point_id = str(uuid.uuid4())

            # Prepare metadata
            metadata = {
                "text": text,
                "timestamp": time.time(),
                "source_id": point_id
            }

            # Add custom metadata if provided
            if metadata_list and i < len(metadata_list):
                metadata.update(metadata_list[i])

            # Create point
            point = models.PointStruct(
                id=point_id,
                vector=embedding,
                payload=metadata
            )
            points.append(point)

            # Create result object
            result = StorageResult(
                embedding_id=point_id,
                metadata=metadata,
                text_content=text
            )
            results.append(result)

        # Upload points to Qdrant
        try:
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points
            )
            self.logger.info(f"Successfully stored {len(points)} embeddings in Qdrant")
        except Exception as e:
            self.logger.error(f"Error storing embeddings in Qdrant: {str(e)}")
            raise

        return results

    def search_similar(self, query_embedding: List[float], limit: int = 10) -> List[SearchResult]:
        """
        Search for similar embeddings in the vector database.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects
        """
        try:
            # Perform similarity search
            search_results = self.client.search(
                collection_name=self.config.collection_name,
                query_vector=query_embedding,
                limit=limit
            )

            # Convert to SearchResult objects
            results = []
            for hit in search_results:
                result = SearchResult(
                    id=hit.id,
                    score=hit.score,
                    payload=hit.payload,
                    vector=hit.vector if hasattr(hit, 'vector') else None
                )
                results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error searching in Qdrant: {str(e)}")
            return []

    def search_by_text_similarity(self, query_text: str, embedder, limit: int = 10) -> List[SearchResult]:
        """
        Search for similar content using text query (generates embedding internally).

        Args:
            query_text: Query text
            embedder: EmbeddingGenerator instance to convert text to embedding
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects
        """
        # Generate embedding for query text
        query_result = embedder.generate_embedding_for_text(query_text)

        if not query_result.is_valid or not query_result.embedding:
            self.logger.error("Failed to generate embedding for query text")
            return []

        # Search using the generated embedding
        return self.search_similar(query_result.embedding, limit)

    def get_embedding_by_id(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an embedding by its ID.

        Args:
            embedding_id: ID of the embedding to retrieve

        Returns:
            Dictionary containing the embedding and metadata, or None if not found
        """
        try:
            records = self.client.retrieve(
                collection_name=self.config.collection_name,
                ids=[embedding_id]
            )

            if records:
                record = records[0]
                return {
                    'id': record.id,
                    'vector': record.vector,
                    'payload': record.payload
                }

        except Exception as e:
            self.logger.error(f"Error retrieving embedding by ID: {str(e)}")

        return None

    def delete_embedding_by_id(self, embedding_id: str) -> bool:
        """
        Delete an embedding by its ID.

        Args:
            embedding_id: ID of the embedding to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.config.collection_name,
                points_selector=models.PointIdsList(
                    points=[embedding_id]
                )
            )
            return True
        except Exception as e:
            self.logger.error(f"Error deleting embedding by ID: {str(e)}")
            return False

    def update_embedding(self, embedding_id: str, new_embedding: List[float],
                        new_payload: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing embedding.

        Args:
            embedding_id: ID of the embedding to update
            new_embedding: New embedding vector
            new_payload: New payload data

        Returns:
            True if successful, False otherwise
        """
        try:
            points = [models.PointStruct(
                id=embedding_id,
                vector=new_embedding,
                payload=new_payload or {}
            )]

            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points
            )
            return True
        except Exception as e:
            self.logger.error(f"Error updating embedding: {str(e)}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection information
        """
        try:
            collection_info = self.client.get_collection(self.config.collection_name)
            return {
                'name': collection_info.config.params.vectors.size,
                'vector_size': collection_info.config.params.vectors.size,
                'distance': collection_info.config.params.vectors.distance,
                'point_count': collection_info.points_count
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            return {}

    def clear_collection(self) -> bool:
        """
        Clear all points from the collection.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all point IDs
            records, _ = self.client.scroll(
                collection_name=self.config.collection_name,
                limit=10000  # Adjust based on expected collection size
            )

            if records:
                point_ids = [record.id for record in records]
                self.client.delete(
                    collection_name=self.config.collection_name,
                    points_selector=models.PointIdsList(points=point_ids)
                )

            return True
        except Exception as e:
            self.logger.error(f"Error clearing collection: {str(e)}")
            return False

    def batch_store_with_retry(self, texts: List[str], embeddings: List[List[float]],
                              metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[StorageResult]:
        """
        Store embeddings with retry logic for failed operations.

        Args:
            texts: Original text chunks
            embeddings: Corresponding embeddings
            metadata_list: Optional list of metadata dictionaries

        Returns:
            List of StorageResult objects
        """
        for attempt in range(self.config.max_retries):
            try:
                return self.store_embeddings(texts, embeddings, metadata_list)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All {self.config.max_retries} attempts failed")
                    raise

        return []