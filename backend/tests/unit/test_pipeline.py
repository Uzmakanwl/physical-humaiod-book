"""
Unit tests for the PipelineManager class.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import time

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.pipeline import PipelineManager


class TestPipelineManager:
    """Test cases for the PipelineManager class."""

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
    def test_initialization(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test PipelineManager initialization."""
        # Verify all components were initialized
        assert self.pipeline.extractor is not None
        assert self.pipeline.validator is not None
        assert self.pipeline.embedder is not None
        assert self.pipeline.storage is not None

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_process_single_url_success(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test successful processing of a single URL."""
        # Configure mocks for success case
        self.mock_validator.validate_before_extraction.return_value = Mock(is_valid=True, errors=[], warnings=[])
        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com',
            'title': 'Test Page',
            'text_content': 'This is test content.',
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

        # Process the URL
        result = self.pipeline.process_single_url('https://example.com')

        # Verify success
        assert result['status'] == 'success'
        assert result['url'] == 'https://example.com'
        assert result['embedding_id'] == 'test-embedding-id'
        assert result['errors'] == []

        # Verify all steps were called
        self.mock_validator.validate_before_extraction.assert_called_once()
        self.mock_extractor.extract_content.assert_called_once()
        self.mock_validator.validate_content.assert_called_once()
        self.mock_embedder.generate_embedding.assert_called_once()
        self.mock_storage.store_embedding.assert_called_once()

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_process_single_url_url_validation_failure(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test processing failure due to URL validation."""
        # Configure validator to fail URL validation
        url_validation_result = Mock()
        url_validation_result.is_valid = False
        url_validation_result.errors = ['Invalid URL format']
        self.mock_validator.validate_before_extraction.return_value = url_validation_result

        # Process the URL
        result = self.pipeline.process_single_url('invalid-url')

        # Verify failure
        assert result['status'] == 'failed'
        assert 'Invalid URL format' in result['errors']

        # Verify that extraction was not called
        self.mock_extractor.extract_content.assert_not_called()

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_process_single_url_content_validation_failure(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test processing failure due to content validation."""
        # Configure mocks
        self.mock_validator.validate_before_extraction.return_value = Mock(is_valid=True, errors=[], warnings=[])
        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com',
            'title': 'Test Page',
            'text_content': 'This is test content.',
            'headings': [],
            'metadata': {}
        }

        # Configure content validation to fail
        content_validation_result = Mock()
        content_validation_result.is_valid = False
        content_validation_result.errors = ['Content quality too low']
        content_validation_result.quality_score = 0.1
        self.mock_validator.validate_content.return_value = content_validation_result

        # Process the URL
        result = self.pipeline.process_single_url('https://example.com', validate_content=True)

        # Verify failure
        assert result['status'] == 'failed'
        assert 'Content quality too low' in result['errors']

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_process_single_url_embedding_validation_failure(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test processing failure due to embedding validation."""
        # Configure mocks
        self.mock_validator.validate_before_extraction.return_value = Mock(is_valid=True, errors=[], warnings=[])
        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com',
            'title': 'Test Page',
            'text_content': 'This is test content.',
            'headings': [],
            'metadata': {}
        }
        self.mock_validator.validate_content.return_value = Mock(is_valid=True, quality_score=0.8)
        self.mock_embedder.generate_embedding.return_value = [0.1, 0.2, 0.3]

        # Configure embedding validation to fail
        self.mock_embedder.validate_embedding_quality.return_value = {
            'is_valid': False,
            'quality_score': 0.1,
            'issues': ['Low quality embedding']
        }

        # Process the URL
        result = self.pipeline.process_single_url('https://example.com')

        # Verify failure
        assert result['status'] == 'failed'
        assert 'Low quality embedding' in str(result['errors'])

    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_process_multiple_urls(self, mock_storage, mock_embedder, mock_validator, mock_extractor):
        """Test processing multiple URLs."""
        urls = ['https://example1.com', 'https://example2.com']

        # Configure mocks for success
        self.mock_validator.validate_before_extraction.return_value = Mock(is_valid=True, errors=[], warnings=[])
        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com',
            'title': 'Test Page',
            'text_content': 'This is test content.',
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
        assert len(results) == 2
        for result in results:
            assert result['status'] == 'success'

    def test_get_pipeline_status(self):
        """Test getting pipeline status."""
        status = self.pipeline.get_pipeline_status()

        # Verify structure of status
        assert 'processing_stats' in status
        assert 'components_status' in status
        assert 'collection_info' in status

        # Verify components status
        components = status['components_status']
        assert all(status == 'ready' for status in components.values())

    def test_monitoring_stats(self):
        """Test monitoring statistics functionality."""
        # Initially, stats should be empty or zero
        stats = self.pipeline.get_monitoring_stats()

        assert 'total_processed' in stats
        assert 'success_rate' in stats
        assert 'average_processing_time' in stats
        assert stats['total_processed'] == 0

        # Reset stats should work
        self.pipeline.reset_monitoring_stats()
        reset_stats = self.pipeline.get_monitoring_stats()
        assert reset_stats['total_processed'] == 0
        assert len(reset_stats['urls_processed']) == 0

    @patch('src.pipeline.time.sleep')  # Mock sleep to speed up tests
    @patch('src.pipeline.ContentExtractor')
    @patch('src.pipeline.ContentValidator')
    @patch('src.pipeline.EmbeddingGenerator')
    @patch('src.pipeline.VectorStorage')
    def test_schedule_processing(self, mock_storage, mock_embedder, mock_validator, mock_extractor, mock_sleep):
        """Test scheduling processing functionality."""
        # Configure mocks
        self.mock_validator.validate_before_extraction.return_value = Mock(is_valid=True, errors=[], warnings=[])
        self.mock_extractor.extract_content.return_value = {
            'url': 'https://example.com',
            'title': 'Test Page',
            'text_content': 'This is test content.',
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

        # Mock sleep to return immediately to avoid actual waiting
        mock_sleep.return_value = None

        # Schedule processing for a short interval (will still be fast due to mocked sleep)
        urls = ['https://example.com']
        scheduler_thread = self.pipeline.schedule_processing(urls, interval_hours=0.0001)  # Very short interval

        # Verify that thread was created
        assert scheduler_thread is not None
        assert scheduler_thread.daemon is True


if __name__ == '__main__':
    pytest.main([__file__])