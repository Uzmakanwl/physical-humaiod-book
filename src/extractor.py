"""
Content extractor module for Docusaurus URL processing.

This module provides functionality to extract content from Docusaurus documentation sites,
preserving document structure and handling various content formats.
"""
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
import logging

from src.models.models import ContentExtractionResult, DocumentStructure


@dataclass
class ExtractionConfig:
    """Configuration for content extraction."""
    timeout: int = 30
    max_retries: int = 3
    allowed_domains: List[str] = None
    headers: Dict[str, str] = None


class ContentExtractor:
    """Content extractor for Docusaurus URL processing."""

    def __init__(self, config: Optional[ExtractionConfig] = None):
        """
        Initialize the content extractor.

        Args:
            config: Extraction configuration (optional)
        """
        self.config = config or ExtractionConfig()
        self.logger = logging.getLogger(__name__)

        if self.config.headers is None:
            self.config.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

    def extract_from_url(self, url: str) -> Optional[ContentExtractionResult]:
        """
        Extract content from a Docusaurus URL.

        Args:
            url: URL to extract content from

        Returns:
            ContentExtractionResult containing the extracted content and metadata
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                self.logger.error(f"Invalid URL: {url}")
                return None

            # Fetch content
            response = self._fetch_content(url)
            if not response:
                self.logger.error(f"Failed to fetch content from {url}")
                return None

            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract document structure
            doc_structure = self._extract_document_structure(soup, url)

            # Extract main content
            text_content = self._extract_text_content(soup)

            # Extract additional elements
            headings = self._extract_headings(soup)
            code_blocks = self._extract_code_blocks(soup)
            lists = self._extract_lists(soup)
            tables = self._extract_tables(soup)
            metadata = self._extract_metadata(soup, url)
            links = self._extract_links(soup, url)

            # Create result object
            result = ContentExtractionResult(
                url=url,
                title=doc_structure.title,
                text_content=text_content,
                headings=headings,
                code_blocks=code_blocks,
                lists=lists,
                tables=tables,
                metadata=metadata,
                links=links
            )

            return result

        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {str(e)}")
            return None

    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if the URL is safe and allowed.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False

            if self.config.allowed_domains:
                if parsed.netloc not in self.config.allowed_domains:
                    return False

            return True
        except Exception:
            return False

    def _fetch_content(self, url: str) -> Optional[requests.Response]:
        """
        Fetch content from URL with retry logic.

        Args:
            url: URL to fetch

        Returns:
            Response object or None if failed
        """
        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.config.headers,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All {self.config.max_retries} attempts failed for {url}")
        return None

    def _extract_document_structure(self, soup: BeautifulSoup, base_url: str) -> DocumentStructure:
        """
        Extract document structure information.

        Args:
            soup: BeautifulSoup object with page content
            base_url: Base URL of the page

        Returns:
            DocumentStructure with hierarchy information
        """
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""

        # Extract headings with hierarchy
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            text = heading.get_text().strip()
            heading_id = heading.get('id', '')

            headings.append({
                'level': level,
                'text': text,
                'id': heading_id
            })

        # Extract content blocks
        content_blocks = []
        for element in soup.find_all(['p', 'div', 'section', 'article', 'main']):
            if element.get_text().strip():
                content_blocks.append({
                    'type': element.name,
                    'content': element.get_text().strip(),
                    'id': element.get('id', '')
                })

        # Extract metadata
        metadata = {
            'title': title,
            'url': base_url,
            'description': '',
            'author': '',
            'date': ''
        }

        # Look for meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            if name == 'description':
                metadata['description'] = content
            elif name == 'author':
                metadata['author'] = content

        return DocumentStructure(
            title=title,
            url=base_url,
            headings=headings,
            content_blocks=content_blocks,
            metadata=metadata,
            breadcrumb_path=self._get_breadcrumb_path(base_url)
        )

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text content from the page.

        Args:
            soup: BeautifulSoup object with page content

        Returns:
            Clean text content
        """
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        # Get text and clean it up
        text = soup.get_text()

        # Break into lines and remove leading/trailing space on each line
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract all headings from the page.

        Args:
            soup: BeautifulSoup object with page content

        Returns:
            List of heading dictionaries
        """
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(heading.name[1]),
                'text': heading.get_text().strip(),
                'id': heading.get('id', ''),
                'class': heading.get('class', [])
            })
        return headings

    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract all code blocks from the page.

        Args:
            soup: BeautifulSoup object with page content

        Returns:
            List of code block dictionaries
        """
        code_blocks = []
        for code in soup.find_all(['code', 'pre']):
            code_text = code.get_text().strip()
            language = code.get('class', [])
            if language:
                # Try to extract language from class (e.g., language-python)
                for cls in language:
                    if cls.startswith('language-'):
                        language = cls.replace('language-', '')
                        break
            else:
                language = 'text'

            code_blocks.append({
                'code': code_text,
                'language': language,
                'type': code.name
            })
        return code_blocks

    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract all lists from the page.

        Args:
            soup: BeautifulSoup object with page content

        Returns:
            List of list dictionaries
        """
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            list_items = []
            for li in ul.find_all('li', recursive=False):
                list_items.append(li.get_text().strip())

            lists.append({
                'type': ul.name,
                'items': list_items,
                'class': ul.get('class', [])
            })
        return lists

    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract all tables from the page.

        Args:
            soup: BeautifulSoup object with page content

        Returns:
            List of table dictionaries
        """
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = []
                for cell in tr.find_all(['td', 'th']):
                    cells.append(cell.get_text().strip())
                if cells:
                    rows.append(cells)

            tables.append({
                'rows': rows,
                'headers': rows[0] if rows else [],
                'class': table.get('class', [])
            })
        return tables

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """
        Extract metadata from the page.

        Args:
            soup: BeautifulSoup object with page content
            url: URL of the page

        Returns:
            Dictionary of metadata
        """
        metadata = {
            'url': url,
            'title': '',
            'description': '',
            'author': '',
            'generator': '',
            'language': ''
        }

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()

        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_name = meta.get('property', '').lower()
            content = meta.get('content', '')

            if name == 'description' or property_name == 'og:description':
                metadata['description'] = content
            elif name == 'author' or property_name == 'article:author':
                metadata['author'] = content
            elif name == 'generator':
                metadata['generator'] = content

        # Extract language
        html_tag = soup.find('html')
        if html_tag:
            metadata['language'] = html_tag.get('lang', '')

        return metadata

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extract all links from the page.

        Args:
            soup: BeautifulSoup object with page content
            base_url: Base URL to resolve relative links

        Returns:
            List of link dictionaries
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            text = link.get_text().strip()

            links.append({
                'text': text,
                'url': full_url,
                'title': link.get('title', ''),
                'class': link.get('class', [])
            })
        return links

    def _get_breadcrumb_path(self, url: str) -> str:
        """
        Generate a breadcrumb path from the URL.

        Args:
            url: URL to generate breadcrumb for

        Returns:
            Breadcrumb path
        """
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part]
        return ' / '.join(path_parts) if path_parts else 'Home'