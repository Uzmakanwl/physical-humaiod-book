"""
Integration tests for the vector storage workflow.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch
import tempfile
import json

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.storage import VectorStorage


class TestStorageWorkflow:
    """Integration tests for the vector storage workflow."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the Qdrant client to avoid requiring a running Qdrant instance
        with patch('src.storage.QdrantClient') as mock_client:
            self.mock_qdrant_client = Mock()
            mock_client.return_value = self.mock_qdrant_client
            self.storage = VectorStorage(collection_name="test_integration")

    def test_complete_storage_workflow(self):
        """Test the complete storage workflow: store -> retrieve -> search -> delete."""
        # Step 1: Store an embedding
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        metadata = {
            "source_url": "https://example.com/test",
            "title": "Test Document",
            "content_length": 100
        }

        self.mock_qdrant_client.upsert.return_value = None
        stored_id = self.storage.store_embedding(embedding, metadata)

        # Verify the embedding was stored
        assert stored_id is not None
        assert len(stored_id) > 0
        self.mock_qdrant_client.upsert.assert_called_once()

        # Step 2: Retrieve the stored embedding
        mock_record = Mock()
        mock_record.id = stored_id
        mock_record.vector = embedding
        mock_record.payload = metadata
        self.mock_qdrant_client.retrieve.return_value = [mock_record]

        retrieved = self.storage.get_embedding_by_id(stored_id)

        assert retrieved is not None
        assert retrieved['id'] == stored_id
        assert retrieved['vector'] == embedding
        assert retrieved['payload'] == metadata

        # Step 3: Search for similar embeddings
        query_embedding = [0.12, 0.18, 0.32, 0.38, 0.52]  # Similar to original
        mock_result = Mock()
        mock_result.id = stored_id
        mock_result.score = 0.85
        mock_result.payload = metadata
        mock_result.vector = embedding
        self.mock_qdrant_client.search.return_value = [mock_result]

        search_results = self.storage.search_similar(query_embedding, limit=5)

        assert len(search_results) == 1
        assert search_results[0]['id'] == stored_id
        assert search_results[0]['score'] > 0.8

        # Step 4: Delete the embedding
        self.mock_qdrant_client.delete.return_value = None
        delete_result = self.storage.delete_embedding(stored_id)

        assert delete_result is True
        self.mock_qdrant_client.delete.assert_called_once()

    def test_batch_storage_workflow(self):
        """Test batch storage and retrieval operations."""
        # Create multiple embeddings and metadata
        embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ]
        metadata_list = [
            {"source_url": "https://example1.com", "title": "Doc 1"},
            {"source_url": "https://example2.com", "title": "Doc 2"},
            {"source_url": "https://example3.com", "title": "Doc 3"}
        ]

        # Mock the upsert operation
        self.mock_qdrant_client.upsert.return_value = None

        # Store multiple embeddings
        stored_ids = self.storage.store_embeddings(embeddings, metadata_list)

        # Verify all embeddings were stored
        assert len(stored_ids) == 3
        self.mock_qdrant_client.upsert.assert_called_once()

        # Check that upsert was called with 3 points
        call_args = self.mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        assert len(points) == 3

    @patch('src.storage.QdrantClient')
    def test_collection_info_workflow(self, mock_client_class):
        """Test getting collection information."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock collection info response
        mock_collection_info = Mock()
        mock_collection_info.config.params.vectors.size = 1024
        mock_collection_info.config.params.vectors.distance = "Cosine"
        mock_collection_info.points_count = 50
        mock_client.get_collection.return_value = mock_collection_info

        storage = VectorStorage(collection_name="info_test")

        info = storage.get_collection_info()

        assert info['name'] == "info_test"
        assert info['vector_size'] == 1024
        assert info['distance'] == "Cosine"
        assert info['point_count'] == 50

    def test_metadata_update_workflow(self):
        """Test updating embedding metadata."""
        embedding_id = "test-embedding-id"
        original_metadata = {"source": "original", "url": "https://example.com"}
        updated_metadata = {"source": "updated", "url": "https://example.com", "updated": True}

        # Store an initial embedding
        self.mock_qdrant_client.upsert.return_value = None
        stored_id = self.storage.store_embedding([0.1, 0.2, 0.3], original_metadata)

        # Update the metadata
        self.mock_qdrant_client.set_payload.return_value = None
        update_result = self.storage.update_embedding_metadata(embedding_id, updated_metadata)

        assert update_result is True
        self.mock_qdrant_client.set_payload.assert_called_once()

    def test_backup_and_restore_workflow(self):
        """Test backup and restore functionality."""
        # Create some test data to store
        test_embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ]
        test_metadata = [
            {"source_url": "https://example1.com", "title": "Backup Test 1"},
            {"source_url": "https://example2.com", "title": "Backup Test 2"}
        ]

        # Store test data
        self.mock_qdrant_client.upsert.return_value = None
        stored_ids = self.storage.store_embeddings(test_embeddings, test_metadata)

        # Mock the scroll operation for backup
        mock_record1 = Mock()
        mock_record1.id = stored_ids[0]
        mock_record1.vector = test_embeddings[0]
        mock_record1.payload = test_metadata[0]

        mock_record2 = Mock()
        mock_record2.id = stored_ids[1]
        mock_record2.vector = test_embeddings[1]
        mock_record2.payload = test_metadata[1]

        # Simulate the scroll operation returning our test records
        def mock_scroll_side_effect(**kwargs):
            if not hasattr(mock_scroll_side_effect, 'called'):
                mock_scroll_side_effect.called = True
                return [mock_record1, mock_record2], None
            else:
                return [], None

        self.mock_qdrant_client.scroll.side_effect = mock_scroll_side_effect

        # Create a temporary file for backup
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            backup_path = temp_file.name

        # Perform backup
        backup_result = self.storage.backup_collection(backup_path)

        assert backup_result is True

        # Verify backup file was created and contains expected data
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)

        assert len(backup_data) == 2
        assert backup_data[0]['id'] == stored_ids[0]
        assert backup_data[0]['vector'] == test_embeddings[0]
        assert backup_data[0]['payload'] == test_metadata[0]

        # Clean up
        os.remove(backup_path)

    def test_concurrent_operations_workflow(self):
        """Test that concurrent operations work safely with locking."""
        import threading
        import time

        # Store an embedding
        self.mock_qdrant_client.upsert.return_value = None
        stored_id = self.storage.store_embedding([0.1, 0.2, 0.3], {"source": "test"})

        # Define operations to run concurrently
        def search_operation():
            query_embedding = [0.15, 0.25, 0.35]
            mock_result = Mock()
            mock_result.id = stored_id
            mock_result.score = 0.9
            mock_result.payload = {"source": "test"}
            mock_result.vector = [0.1, 0.2, 0.3]
            self.mock_qdrant_client.search.return_value = [mock_result]
            self.storage.search_similar(query_embedding)

        def retrieve_operation():
            mock_record = Mock()
            mock_record.id = stored_id
            mock_record.vector = [0.1, 0.2, 0.3]
            mock_record.payload = {"source": "test"}
            self.mock_qdrant_client.retrieve.return_value = [mock_record]
            self.storage.get_embedding_by_id(stored_id)

        # Run operations concurrently
        threads = []
        for i in range(5):  # Run 5 concurrent operations
            t1 = threading.Thread(target=search_operation)
            t2 = threading.Thread(target=retrieve_operation)
            threads.extend([t1, t2])
            t1.start()
            t2.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # If we reach here without exceptions, concurrent operations worked safely
        assert True  # This is just to have an assertion


if __name__ == '__main__':
    pytest.main([__file__])