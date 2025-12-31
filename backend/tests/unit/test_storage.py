"""
Unit tests for the VectorStorage class.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.storage import VectorStorage


class TestVectorStorage:
    """Test cases for the VectorStorage class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the Qdrant client to avoid requiring a running Qdrant instance
        with patch('src.storage.QdrantClient') as mock_client:
            self.mock_qdrant_client = Mock()
            mock_client.return_value = self.mock_qdrant_client
            self.storage = VectorStorage(collection_name="test_collection")

    @patch('src.storage.QdrantClient')
    def test_initialization(self, mock_client_class):
        """Test VectorStorage initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock collection existence check
        mock_client.get_collection.side_effect = Exception("Collection doesn't exist")
        # Mock collection creation
        storage = VectorStorage(collection_name="test_init")

        assert storage.collection_name == "test_init"
        assert storage.client == mock_client

    def test_store_single_embedding(self):
        """Test storing a single embedding."""
        from qdrant_client.http import models

        # Mock the upsert operation
        self.mock_qdrant_client.upsert.return_value = None

        embedding = [0.1, 0.2, 0.3]
        metadata = {"source": "test", "url": "https://example.com"}

        result_id = self.storage.store_embedding(embedding, metadata)

        # Check that upsert was called with the correct parameters
        assert len(result_id) > 0  # Should return a valid ID
        self.mock_qdrant_client.upsert.assert_called_once()

        # Get the arguments passed to upsert
        call_args = self.mock_qdrant_client.upsert.call_args
        assert call_args[1]['collection_name'] == "test_collection"

        points = call_args[1]['points']
        assert len(points) == 1
        point = points[0]
        assert point.id == result_id
        assert point.vector == embedding
        assert point.payload['source'] == "test"
        assert point.payload['url'] == "https://example.com"

    def test_store_multiple_embeddings(self):
        """Test storing multiple embeddings."""
        self.mock_qdrant_client.upsert.return_value = None

        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        metadata_list = [
            {"source": "test1", "url": "https://example1.com"},
            {"source": "test2", "url": "https://example2.com"}
        ]

        result_ids = self.storage.store_embeddings(embeddings, metadata_list)

        assert len(result_ids) == 2
        self.mock_qdrant_client.upsert.assert_called_once()

        # Check that upsert was called with multiple points
        call_args = self.mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        assert len(points) == 2

    def test_store_embeddings_mismatched_lengths(self):
        """Test storing embeddings with mismatched metadata list length."""
        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        metadata_list = [{"source": "test1"}]  # One less than embeddings

        with pytest.raises(ValueError):
            self.storage.store_embeddings(embeddings, metadata_list)

    def test_search_similar(self):
        """Test searching for similar embeddings."""
        from qdrant_client.http import models

        # Mock search results
        mock_result = Mock()
        mock_result.id = "mock_id_1"
        mock_result.score = 0.9
        mock_result.payload = {"source": "test", "url": "https://example.com"}
        mock_result.vector = [0.1, 0.2]

        self.mock_qdrant_client.search.return_value = [mock_result]

        query_embedding = [0.15, 0.25]
        results = self.storage.search_similar(query_embedding, limit=5)

        assert len(results) == 1
        assert results[0]['id'] == "mock_id_1"
        assert results[0]['score'] == 0.9
        assert results[0]['payload']['source'] == "test"

        # Check that search was called with correct parameters
        self.mock_qdrant_client.search.assert_called_once()
        call_args = self.mock_qdrant_client.search.call_args
        assert call_args[1]['collection_name'] == "test_collection"
        assert call_args[1]['query_vector'] == query_embedding
        assert call_args[1]['limit'] == 5

    def test_get_embedding_by_id(self):
        """Test retrieving an embedding by ID."""
        from qdrant_client.http import models

        # Mock retrieve results
        mock_record = Mock()
        mock_record.id = "test_id"
        mock_record.vector = [0.1, 0.2, 0.3]
        mock_record.payload = {"source": "test", "url": "https://example.com"}

        self.mock_qdrant_client.retrieve.return_value = [mock_record]

        result = self.storage.get_embedding_by_id("test_id")

        assert result is not None
        assert result['id'] == "test_id"
        assert result['vector'] == [0.1, 0.2, 0.3]
        assert result['payload']['source'] == "test"

        # Check that retrieve was called correctly
        self.mock_qdrant_client.retrieve.assert_called_once()
        call_args = self.mock_qdrant_client.retrieve.call_args
        assert call_args[1]['collection_name'] == "test_collection"
        assert call_args[1]['ids'] == ["test_id"]

    def test_get_embedding_by_id_not_found(self):
        """Test retrieving an embedding that doesn't exist."""
        self.mock_qdrant_client.retrieve.return_value = []

        result = self.storage.get_embedding_by_id("nonexistent_id")

        assert result is None

    def test_delete_embedding(self):
        """Test deleting an embedding."""
        from qdrant_client.http import models

        self.mock_qdrant_client.delete.return_value = None

        result = self.storage.delete_embedding("test_id")

        assert result is True
        self.mock_qdrant_client.delete.assert_called_once()

        call_args = self.mock_qdrant_client.delete.call_args
        assert call_args[1]['collection_name'] == "test_collection"
        points_selector = call_args[1]['points_selector']
        # Check that the points selector contains the correct ID
        assert "test_id" in str(points_selector)

    def test_get_collection_info(self):
        """Test getting collection information."""
        # Mock collection info
        mock_collection_info = Mock()
        mock_collection_info.config.params.vectors.size = 1536
        mock_collection_info.config.params.vectors.distance = "Cosine"
        mock_collection_info.points_count = 100

        self.mock_qdrant_client.get_collection.return_value = mock_collection_info

        info = self.storage.get_collection_info()

        assert info['name'] == "test_collection"
        assert info['vector_size'] == 1536
        assert info['distance'] == "Cosine"
        assert info['point_count'] == 100

    def test_update_embedding_metadata(self):
        """Test updating embedding metadata."""
        from qdrant_client.http import models

        self.mock_qdrant_client.set_payload.return_value = None

        new_metadata = {"updated": "true", "new_field": "value"}
        result = self.storage.update_embedding_metadata("test_id", new_metadata)

        assert result is True
        self.mock_qdrant_client.set_payload.assert_called_once()

        call_args = self.mock_qdrant_client.set_payload.call_args
        assert call_args[1]['collection_name'] == "test_collection"
        assert call_args[1]['payload'] == new_metadata
        points_selector = call_args[1]['points_selector']
        # Check that the points selector contains the correct ID
        assert "test_id" in str(points_selector)


if __name__ == '__main__':
    pytest.main([__file__])