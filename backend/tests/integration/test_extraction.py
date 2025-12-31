"""
Integration tests for the content extraction workflow.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.extractor import ContentExtractor
from src.validator import ContentValidator
from src.validators import validate_url, is_safe_url


class TestExtractionWorkflow:
    """Integration tests for the content extraction workflow."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.extractor = ContentExtractor(timeout=10)
        self.validator = ContentValidator()

    @patch('src.extractor.requests.Session.get')
    def test_complete_extraction_workflow(self, mock_get):
        """Test the complete workflow: validation -> extraction -> content validation."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <head>
                <title>Integration Test Page</title>
                <meta name="description" content="Test page for integration">
            </head>
            <body>
                <main>
                    <h1>Main Heading</h1>
                    <p>This is the main content for integration testing.</p>
                    <h2>Subsection</h2>
                    <p>Additional content in subsection.</p>
                    <code>const x = 1;</code>
                    <ul>
                        <li>First item</li>
                        <li>Second item</li>
                    </ul>
                </main>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Step 1: Validate URL before extraction
        url = 'https://example.com/test-page'
        url_validation = self.validator.validate_before_extraction(url)
        assert url_validation.is_valid

        # Step 2: Extract content
        extracted_content = self.extractor.extract_content(url)

        # Assertions for extracted content
        assert extracted_content['url'] == url
        assert extracted_content['title'] == 'Integration Test Page'
        assert 'main content' in extracted_content['text_content'].lower()
        assert len(extracted_content['headings']) > 0
        assert len(extracted_content['code_blocks']) > 0

        # Step 3: Validate extracted content
        content_validation = self.validator.validate_content(extracted_content)
        assert content_validation.is_valid
        assert content_validation.quality_score > 0.5

    @patch('src.extractor.requests.Session.get')
    def test_extraction_with_structure_preservation(self, mock_get):
        """Test extraction with proper structure preservation."""
        # Mock response with complex structure
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <head><title>Structured Test</title></head>
            <body>
                <main>
                    <h1>Introduction</h1>
                    <p>Introductory content.</p>
                    <h2>Section 1</h2>
                    <p>Content for section 1.</p>
                    <h3>Subsection 1.1</h3>
                    <p>Content for subsection 1.1.</p>
                    <h2>Section 2</h2>
                    <p>Content for section 2.</p>
                </main>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        extracted_content = self.extractor.extract_content('https://example.com/structured')

        # Check that headings are properly extracted with hierarchy
        headings = extracted_content['headings']
        assert len(headings) == 4  # h1, h2, h3, h2
        assert any(h['level'] == 1 for h in headings)  # Has h1
        assert any(h['level'] == 2 for h in headings)  # Has h2
        assert any(h['level'] == 3 for h in headings)  # Has h3

    @patch('src.extractor.requests.Session.get')
    def test_extraction_validation_pipeline(self, mock_get):
        """Test the full validation pipeline."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '<html><head><title>Valid Page</title></head><body><p>Valid content here.</p></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        url = 'https://example.com/valid-page'

        # Validate URL
        url_validation = self.validator.validate_before_extraction(url)
        assert url_validation.is_valid, f"URL validation failed: {url_validation.errors}"

        # Validate URL format with utility function
        assert validate_url(url), "Utility URL validation failed"
        assert is_safe_url(url), "Utility safety validation failed"

        # Extract content
        extracted_content = self.extractor.extract_content(url)

        # Validate extracted content
        content_validation = self.validator.validate_content(extracted_content)
        assert content_validation.is_valid, f"Content validation failed: {content_validation.errors}"
        assert content_validation.quality_score > 0.0, "Content quality score is too low"

    @patch('src.extractor.requests.Session.get')
    def test_extraction_with_code_and_tables(self, mock_get):
        """Test extraction of code blocks and tables."""
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <body>
                <h1>Code and Tables Test</h1>
                <pre><code>function test() {
                    return "hello world";
                }</code></pre>
                <table>
                    <tr><th>Name</th><th>Value</th></tr>
                    <tr><td>Item 1</td><td>100</td></tr>
                    <tr><td>Item 2</td><td>200</td></tr>
                </table>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        extracted_content = self.extractor.extract_content('https://example.com/code-tables')

        # Check that code blocks and tables are extracted
        assert len(extracted_content['code_blocks']) > 0, "Code blocks not extracted"
        assert len(extracted_content['tables']) > 0, "Tables not extracted"
        assert len(extracted_content['tables'][0]['rows']) == 3, "Table rows not properly extracted"

    def test_invalid_url_workflow(self):
        """Test workflow with invalid URLs."""
        # Test with invalid URL
        invalid_url = 'not-a-url'

        url_validation = self.validator.validate_before_extraction(invalid_url)
        assert not url_validation.is_valid
        assert 'Invalid URL format' in url_validation.errors[0]

        # Test with utility validators
        assert not validate_url(invalid_url), "Utility should detect invalid URL"
        assert not is_safe_url(invalid_url), "Utility should detect unsafe URL"


if __name__ == '__main__':
    pytest.main([__file__])