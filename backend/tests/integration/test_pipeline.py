"""
Integration tests for the complete pipeline workflow.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.pipeline import PipelineManager


class TestPipelineIntegration:
    """Integration tests for the complete pipeline workflow."""

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def setup_method(self, method, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Set up test fixtures before each test method."""
        # Setup all mocked dependencies
        self.mock_extractor = Mock()
        self.mock_validator = Mock()
        self.mock_embedder = Mock()
        self.mock_storage = Mock()

        # Configure the mocks
        mock_extractor.return_value = self.mock_extractor
        mock_validator.return_value = self.mock_validator
        mock_embedder.return_value = self.mock_embedder
        mock_storage.return_value = self.mock_storage

        self.pipeline = PipelineManager()

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_complete_pipeline_workflow(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test the complete end-to-end pipeline workflow."""
        # Configure all mocks for a successful flow
        self.mock_validator.validate_before_extraction.return_value = Mock(is_valid=True, errors=[], warnings=[])
        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com/doc',
            'title': 'Example Documentation',
            'text_content': 'This is example documentation content for testing the complete pipeline workflow.',
            'headings': [
                {'level': 1, 'text': 'Main Heading', 'id': 'main'},
                {'level': 2, 'text': 'Sub Heading', 'id': 'sub'}
            ],
            'code_blocks': [{'language': ['language-python'], 'content': 'print("hello world")'}],
            'lists': [{'type': 'unordered', 'items': ['item 1', 'item 2']}],
            'tables': [{'rows': [['Header 1', 'Header 2'], ['Cell 1', 'Cell 2']]}],
            'metadata': {'description': 'Test description', 'author': 'Test Author'},
            'links': [{'text': 'Example Link', 'url': 'https://example.com/link'}]
        }
        self.mock_validator.validate_content.return_value = Mock(is_valid=True, quality_score=0.85, errors=[], warnings=[])
        self.mock_embedder.generate_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_embedder.validate_embedding_quality.return_value = {
            'is_valid': True,
            'quality_score': 0.9,
            'issues': [],
            'metrics': {'magnitude': 0.5, 'avg_abs_value': 0.2, 'dimension': 5}
        }
        self.mock_storage.store_embedding.return_value = 'test-embedding-id-123'

        # Execute the complete pipeline
        result = self.pipeline.process_single_url('https://example.com/doc')

        # Verify the result
        assert result['status'] == 'success'
        assert result['url'] == 'https://example.com/doc'
        assert result['embedding_id'] == 'test-embedding-id-123'
        assert result['extracted_content']['title'] == 'Example Documentation'
        assert len(result['extracted_content']['headings']) == 2
        assert result['errors'] == []

        # Verify all components were called in the correct sequence
        self.mock_validator.validate_before_extraction.assert_called_once_with('https://example.com/doc')
        self.mock_extractor.extract_content.assert_called_once_with('https://example.com/doc')
        self.mock_validator.validate_content.assert_called_once()
        self.mock_embedder.generate_embedding.assert_called_once()
        self.mock_storage.store_embedding.assert_called_once()

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_pipeline_with_multiple_urls(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test processing multiple URLs through the pipeline."""
        urls = [
            'https://example.com/page1',
            'https://example.com/page2',
            'https://example.com/page3'
        ]

        # Configure mocks for successful processing of all URLs
        self.mock_validator.validate_before_extraction.return_value = Mock(is_valid=True, errors=[], warnings=[])
        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com/page',
            'title': 'Test Page',
            'text_content': 'Test content',
            'headings': [],
            'metadata': {}
        }
        self.mock_validator.validate_content.return_value = Mock(is_valid=True, quality_score=0.8)
        self.mock_embedder.generate_embedding.return_value = [0.1, 0.2, 0.3]
        self.mock_embedder.validate_embedding_quality.return_value = {
            'is_valid': True,
            'quality_score': 0.9,
            'issues': []
        }
        self.mock_storage.store_embedding.return_value = 'test-embedding-id'

        # Process multiple URLs
        results = self.pipeline.process_multiple_urls(urls, max_workers=2)

        # Verify results
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result['status'] == 'success'
            assert result['url'] == urls[i]
            assert result['embedding_id'] == 'test-embedding-id'
            assert result['errors'] == []

        # Verify that extraction was called for each URL
        assert self.mock_extractor.extract_content.call_count == 3

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_pipeline_with_mixed_results(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test pipeline with some successful and some failed URLs."""
        urls = [
            'https://example.com/success',
            'https://example.com/failure',
            'https://example.com/success2'
        ]

        # Configure mocks
        self.mock_validator.validate_before_extraction.side_effect = [
            Mock(is_valid=True, errors=[], warnings=[]),  # success URL
            Mock(is_valid=False, errors=['Invalid URL'], warnings=[]),  # failure URL
            Mock(is_valid=True, errors=[], warnings=[])   # success2 URL
        ]

        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com/page',
            'title': 'Test Page',
            'text_content': 'Test content',
            'headings': [],
            'metadata': {}
        }
        self.mock_validator.validate_content.return_value = Mock(is_valid=True, quality_score=0.8)
        self.mock_embedder.generate_embedding.return_value = [0.1, 0.2, 0.3]
        self.mock_embedder.validate_embedding_quality.return_value = {
            'is_valid': True,
            'quality_score': 0.9,
            'issues': []
        }
        self.mock_storage.store_embedding.return_value = 'test-embedding-id'

        # Process URLs with mixed results
        results = self.pipeline.process_multiple_urls(urls, max_workers=1)

        # Verify results
        assert len(results) == 3
        assert results[0]['status'] == 'success'
        assert results[1]['status'] == 'failed'
        assert results[2]['status'] == 'success'

        assert 'Invalid URL' in results[1]['errors']

    def test_pipeline_monitoring_and_stats(self):
        """Test pipeline monitoring and statistics."""
        # Initially, stats should be empty
        initial_stats = self.pipeline.get_monitoring_stats()
        assert initial_stats['total_processed'] == 0
        assert initial_stats['total_errors'] == 0

        # After processing, stats should update
        # (This test would require actual processing which is mocked in other tests)

        # Test stats reset
        self.pipeline.reset_monitoring_stats()
        reset_stats = self.pipeline.get_monitoring_stats()
        assert reset_stats['total_processed'] == 0
        assert reset_stats['total_errors'] == 0

    def test_pipeline_health_check(self):
        """Test pipeline health validation."""
        health = self.pipeline.validate_pipeline_health()

        # Health check should return a structured response
        assert 'extractor' in health
        assert 'validator' in health
        assert 'embedder' in health
        assert 'storage' in health
        assert 'overall' in health
        assert 'issues' in health

        # In our mocked environment, the embedder might fail due to missing API key
        # which is expected behavior
        if not health['embedder']:
            assert 'COHERE_API_KEY not configured' in str(health['issues'])

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_pipeline_search_functionality(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test the search functionality through the pipeline."""
        # Configure mocks for search test
        self.mock_embedder.generate_embedding.return_value = [0.1, 0.2, 0.3]

        mock_search_result = Mock()
        mock_search_result.id = 'search-result-id'
        mock_search_result.score = 0.85
        mock_search_result.payload = {'source_url': 'https://example.com', 'title': 'Test Document'}
        mock_search_result.vector = [0.1, 0.2, 0.3]

        self.mock_storage.search_similar.return_value = [mock_search_result]

        # Test search functionality
        results = self.pipeline.search_similar_content('test query about documentation', limit=5)

        # Verify search was performed
        assert len(results) == 1
        assert results[0]['id'] == 'search-result-id'
        assert results[0]['score'] == 0.85
        assert results[0]['payload']['title'] == 'Test Document'

        # Verify embedder and storage were called
        self.mock_embedder.generate_embedding.assert_called_once_with('test query about documentation')
        self.mock_storage.search_similar.assert_called_once()

    def test_pipeline_status_report(self):
        """Test pipeline status reporting."""
        status = self.pipeline.get_pipeline_status()

        # Verify the structure of the status report
        assert 'processing_stats' in status
        assert 'components_status' in status
        assert 'collection_info' in status

        # Verify components status
        components_status = status['components_status']
        assert all(status == 'ready' for status in components_status.values())


if __name__ == '__main__':
    pytest.main([__file__])