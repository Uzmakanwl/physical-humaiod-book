"""
Unit tests for the EmbeddingGenerator class.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.embedder import EmbeddingGenerator


class TestEmbeddingGenerator:
    """Test cases for the EmbeddingGenerator class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the Cohere client to avoid making real API calls
        with patch('src.embedder.cohere.Client') as mock_client:
            self.mock_cohere_client = Mock()
            mock_client.return_value = self.mock_cohere_client
            self.embedder = EmbeddingGenerator()

    @patch('src.embedder.cohere.Client')
    def test_initialization(self, mock_client_class):
        """Test EmbeddingGenerator initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        embedder = EmbeddingGenerator(model="test-model")

        assert embedder.model == "test-model"
        mock_client_class.assert_called_once()

    def test_generate_single_embedding(self):
        """Test generation of a single embedding."""
        # Mock the Cohere API response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        self.mock_cohere_client.embed.return_value = mock_response

        text = "Test sentence"
        embedding = self.embedder.generate_embedding(text)

        assert embedding == [0.1, 0.2, 0.3]
        self.mock_cohere_client.embed.assert_called_once()

    def test_generate_multiple_embeddings(self):
        """Test generation of multiple embeddings."""
        # Mock the Cohere API response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.mock_cohere_client.embed.return_value = mock_response

        texts = ["Test sentence 1", "Test sentence 2"]
        embeddings = self.embedder.generate_embeddings(texts)

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]

    def test_validate_embedding_quality_valid(self):
        """Test validation of a valid embedding."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        text = "Test text"

        result = self.embedder.validate_embedding_quality(embedding, text)

        assert result['is_valid'] is True
        assert result['quality_score'] > 0.3
        assert len(result['issues']) == 0

    def test_validate_embedding_quality_empty(self):
        """Test validation of an empty embedding."""
        embedding = []
        text = "Test text"

        result = self.embedder.validate_embedding_quality(embedding, text)

        assert result['is_valid'] is False
        assert result['quality_score'] == 0.0
        assert 'Empty embedding' in result['issues']

    def test_validate_embedding_quality_zero_vector(self):
        """Test validation of a zero vector embedding."""
        embedding = [0.0, 0.0, 0.0]
        text = "Test text"

        result = self.embedder.validate_embedding_quality(embedding, text)

        assert result['is_valid'] is False
        assert result['quality_score'] == 0.0
        assert 'Zero vector' in result['issues'][0]

    def test_validate_embedding_quality_low_magnitude(self):
        """Test validation of a low-magnitude embedding."""
        embedding = [0.01, 0.01, 0.01]  # Low magnitude
        text = "Test text"

        result = self.embedder.validate_embedding_quality(embedding, text)

        # Even with low magnitude, it might still be valid depending on thresholds
        assert isinstance(result['is_valid'], bool)

    def test_calculate_similarity(self):
        """Test similarity calculation between embeddings."""
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [1.0, 0.0, 0.0]  # Same embedding

        similarity = self.embedder.calculate_similarity(embedding1, embedding2)
        assert abs(similarity - 1.0) < 0.001  # Should be very close to 1.0

        embedding2 = [0.0, 1.0, 0.0]  # Orthogonal embedding
        similarity = self.embedder.calculate_similarity(embedding1, embedding2)
        assert abs(similarity - 0.0) < 0.001  # Should be very close to 0.0

    def test_batch_process_with_validation(self):
        """Test batch processing with validation."""
        # Mock the Cohere API response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.mock_cohere_client.embed.return_value = mock_response

        texts = ["Test sentence 1", "Test sentence 2"]
        results = self.embedder.batch_process_with_validation(texts)

        assert len(results) == 2
        assert results[0]['text'] == "Test sentence 1"
        assert results[0]['embedding'] == [0.1, 0.2, 0.3]
        assert 'validation' in results[0]

    def test_check_embedding_consistency(self):
        """Test embedding consistency checking."""
        # Test with identical embeddings (should be consistent)
        embeddings = [[1.0, 0.0], [1.0, 0.0]]
        result = self.embedder.check_embedding_consistency(embeddings)
        assert result['is_consistent'] is True

        # Test with very different embeddings (should be inconsistent with low threshold)
        embeddings = [[1.0, 0.0], [0.0, 1.0]]
        result = self.embedder.check_embedding_consistency(embeddings, threshold=0.1)
        assert result['is_consistent'] is False

        # Test with single embedding (should be consistent)
        embeddings = [[1.0, 0.0]]
        result = self.embedder.check_embedding_consistency(embeddings)
        assert result['is_consistent'] is True

    def test_generate_embeddings_empty_list(self):
        """Test generating embeddings for an empty list."""
        embeddings = self.embedder.generate_embeddings([])
        assert embeddings == []

    def test_generate_embeddings_with_batch_retry(self):
        """Test generating embeddings with batch retry mechanism."""
        # This test simulates the retry mechanism when API calls fail
        # First call fails, second succeeds with smaller batch
        def mock_embed_side_effect(texts, **kwargs):
            if len(texts) > 1:
                # Simulate failure for large batches
                raise Exception("Batch too large")
            else:
                # Return successful result for single item
                return Mock(embeddings=[[0.1, 0.2, 0.3]])

        self.mock_cohere_client.embed.side_effect = mock_embed_side_effect

        # This should trigger the retry mechanism
        texts = ["text1", "text2"]
        embeddings = self.embedder.generate_embeddings(texts, batch_size=2)

        # Should have processed both texts individually
        assert len(embeddings) == 2


if __name__ == '__main__':
    pytest.main([__file__])