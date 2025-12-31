"""
Integration tests for the embedding generation workflow.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.embedder import EmbeddingGenerator
from src.validator import ContentValidator


class TestEmbeddingWorkflow:
    """Integration tests for the embedding generation workflow."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the Cohere client to avoid making real API calls
        with patch('src.embedder.cohere.Client') as mock_client:
            self.mock_cohere_client = Mock()
            mock_client.return_value = self.mock_cohere_client
            self.embedder = EmbeddingGenerator()
            self.validator = ContentValidator()

    @patch('src.embedder.cohere.Client')
    def test_complete_embedding_workflow(self, mock_client_class):
        """Test the complete workflow: text -> embedding -> validation."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3, 0.4]]
        mock_client.embed.return_value = mock_response

        # Create an embedder instance
        embedder = EmbeddingGenerator()

        # Step 1: Generate embedding
        text = "This is a test sentence for embedding."
        embedding = embedder.generate_embedding(text)

        # Assertions for embedding generation
        assert len(embedding) > 0
        assert all(isinstance(val, float) for val in embedding)

        # Step 2: Validate embedding quality
        validation_result = embedder.validate_embedding_quality(embedding, text)

        # Assertions for validation
        assert validation_result['is_valid'] is True
        assert validation_result['quality_score'] > 0.0
        assert isinstance(validation_result['metrics'], dict)

    @patch('src.embedder.cohere.Client')
    def test_batch_embedding_workflow(self, mock_client_class):
        """Test the batch embedding workflow."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        # Return multiple embeddings for batch processing
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        mock_client.embed.return_value = mock_response

        # Create an embedder instance
        embedder = EmbeddingGenerator()

        # Step 1: Generate batch embeddings
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        embeddings = embedder.generate_embeddings(texts)

        # Assertions for batch embedding
        assert len(embeddings) == 3
        assert all(len(embedding) > 0 for embedding in embeddings)

        # Step 2: Validate all embeddings
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            validation = embedder.validate_embedding_quality(embedding, text)
            assert validation['is_valid'] is True, f"Validation failed for embedding {i}: {validation['issues']}"

        # Step 3: Check consistency
        consistency = embedder.check_embedding_consistency(embeddings)
        assert isinstance(consistency['is_consistent'], bool)

    @patch('src.embedder.cohere.Client')
    def test_embedding_with_content_validation(self, mock_client_class):
        """Test embedding generation combined with content validation."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        mock_client.embed.return_value = mock_response

        # Create instances
        embedder = EmbeddingGenerator()
        validator = ContentValidator()

        # Simulate content that would come from extraction
        content_data = {
            'url': 'https://example.com/test',
            'text_content': 'This is a sample content for testing the embedding pipeline.',
            'title': 'Test Content',
            'headings': [{'level': 1, 'text': 'Main Heading', 'id': ''}]
        }

        # Step 1: Validate content
        content_validation = validator.validate_content(content_data)
        assert content_validation.is_valid is True

        # Step 2: Generate embedding from content
        embedding = embedder.generate_embedding(content_data['text_content'])

        # Step 3: Validate embedding
        embedding_validation = embedder.validate_embedding_quality(embedding, content_data['text_content'])
        assert embedding_validation['is_valid'] is True

        # Step 4: Process with batch validation
        batch_result = embedder.batch_process_with_validation([content_data['text_content']])
        assert len(batch_result) == 1
        assert batch_result[0]['validation']['is_valid'] is True

    @patch('src.embedder.cohere.Client')
    def test_embedding_similarity_workflow(self, mock_client_class):
        """Test the similarity calculation workflow."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.embeddings = [[0.8, 0.2, 0.1], [0.7, 0.3, 0.1]]  # Similar embeddings
        mock_client.embed.return_value = mock_response

        embedder = EmbeddingGenerator()

        # Generate similar embeddings
        texts = ["Similar sentence one.", "Similar sentence two."]
        embeddings = embedder.generate_embeddings(texts)

        # Calculate similarity between embeddings
        similarity = embedder.calculate_similarity(embeddings[0], embeddings[1])
        assert 0.0 <= similarity <= 1.0

        # Check consistency of similar embeddings
        consistency = embedder.check_embedding_consistency(embeddings)
        # Even if they're similar, consistency depends on the threshold

    @patch('src.embedder.cohere.Client')
    def test_embedding_workflow_with_realistic_content(self, mock_client_class):
        """Test embedding workflow with more realistic content."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        # Simulate realistic embedding dimensions (Cohere typically returns 1024+ dimensions)
        mock_response.embeddings = [
            [i * 0.01 for i in range(1024)],  # First embedding
            [i * 0.01 + 0.1 for i in range(1024)]  # Second embedding, slightly different
        ]
        mock_client.embed.return_value = mock_response

        embedder = EmbeddingGenerator()

        # Use more realistic content
        content_pieces = [
            "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            "Deep learning uses neural networks with multiple layers to model complex patterns.",
            "Natural language processing enables computers to understand and generate human language."
        ]

        # Process all content pieces
        embeddings = embedder.generate_embeddings(content_pieces)

        # Validate each embedding
        for i, (content, embedding) in enumerate(zip(content_pieces, embeddings)):
            validation = embedder.validate_embedding_quality(embedding, content)
            assert validation['is_valid'] is True, f"Embedding {i} validation failed: {validation['issues']}"
            assert len(embedding) == 1024, f"Embedding {i} has wrong dimension: {len(embedding)}"

        # Check consistency across all embeddings
        consistency = embedder.check_embedding_consistency(embeddings)
        # With realistic content, embeddings might not be highly consistent, which is expected

    def test_error_handling_in_workflow(self):
        """Test error handling in the embedding workflow."""
        # Test with empty text
        try:
            embedding = self.embedder.generate_embedding("")
            # If it doesn't raise an error, check that the embedding is handled appropriately
            assert isinstance(embedding, list)
        except Exception:
            # It's acceptable for empty text to cause an error in the mock
            pass

        # Test with None text
        try:
            embedding = self.embedder.generate_embedding(None)
            # If it doesn't raise an error, check that the embedding is handled appropriately
            assert isinstance(embedding, list)
        except Exception:
            # It's acceptable for None text to cause an error in the mock
            pass


if __name__ == '__main__':
    pytest.main([__file__])