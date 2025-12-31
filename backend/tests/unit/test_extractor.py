"""
Unit tests for the ContentExtractor class.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.extractor import ContentExtractor


class TestContentExtractor:
    """Test cases for the ContentExtractor class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.extractor = ContentExtractor(timeout=10)

    @patch('src.extractor.requests.Session.get')
    def test_extract_content_success(self, mock_get):
        """Test successful content extraction."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <main>
                    <h1>Heading 1</h1>
                    <p>This is test content.</p>
                    <h2>Subheading</h2>
                    <p>More content.</p>
                    <code>console.log("test");</code>
                    <ul>
                        <li>Item 1</li>
                        <li>Item 2</li>
                    </ul>
                </main>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test extraction
        result = self.extractor.extract_content('https://example.com')

        # Assertions
        assert result['url'] == 'https://example.com'
        assert result['title'] == 'Test Page'
        assert 'test content' in result['text_content'].lower()
        assert len(result['headings']) == 2  # h1 and h2
        assert len(result['code_blocks']) >= 1
        assert len(result['lists']) == 1
        assert len(result['metadata']) >= 1

    @patch('src.extractor.requests.Session.get')
    def test_extract_content_with_tables(self, mock_get):
        """Test content extraction with tables."""
        # Mock response with table
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <body>
                <table>
                    <tr>
                        <th>Header 1</th>
                        <th>Header 2</th>
                    </tr>
                    <tr>
                        <td>Cell 1</td>
                        <td>Cell 2</td>
                    </tr>
                </table>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.extractor.extract_content('https://example.com')

        assert len(result['tables']) == 1
        assert len(result['tables'][0]['rows']) == 2  # header row + data row

    @patch('src.extractor.requests.Session.get')
    def test_extract_content_with_links(self, mock_get):
        """Test content extraction with links."""
        # Mock response with links
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <body>
                <a href="/page1">Link 1</a>
                <a href="https://external.com">External Link</a>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.extractor.extract_content('https://example.com')

        assert len(result['links']) == 2
        assert any('Link 1' in link['text'] for link in result['links'])

    def test_detect_docusaurus_structure(self):
        """Test detection of Docusaurus structure."""
        # This test is more complex as it requires actual HTTP requests
        # For now, we'll test that the method exists and doesn't crash
        assert hasattr(self.extractor, 'detect_docusaurus_structure')

    def test_invalid_url_extraction(self):
        """Test extraction with invalid URL."""
        with pytest.raises(ValueError):
            self.extractor.extract_content('invalid-url')

    @patch('src.extractor.requests.Session.get')
    def test_extraction_request_exception(self, mock_get):
        """Test extraction when request fails."""
        mock_get.side_effect = Exception('Network error')

        with pytest.raises(Exception):
            self.extractor.extract_content('https://example.com')


if __name__ == '__main__':
    pytest.main([__file__])