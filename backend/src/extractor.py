"""
Content extractor module for the embedding pipeline.

This module handles extraction of text content from Docusaurus URLs,
preserving document structure and formatting elements.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
import logging

from src.logger import get_logger
from src.validators import validate_url


class ContentExtractor:
    """Extracts content from Docusaurus URLs while preserving document structure."""

    def __init__(self, timeout: int = 30):
        """
        Initialize the ContentExtractor.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.logger = get_logger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_content(self, url: str) -> Dict[str, any]:
        """
        Extract content from a Docusaurus URL.

        Args:
            url: The URL to extract content from

        Returns:
            Dictionary containing extracted content and metadata
        """
        # Validate the URL first
        if not validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        try:
            # Fetch the content
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content preserving structure
            content_data = {
                'url': url,
                'title': self._extract_title(soup),
                'text_content': self._extract_text_content(soup),
                'headings': self._extract_headings(soup),
                'code_blocks': self._extract_code_blocks(soup),
                'lists': self._extract_lists(soup),
                'tables': self._extract_tables(soup),
                'metadata': self._extract_metadata(soup),
                'links': self._extract_links(soup, url)
            }

            self.logger.info(f"Successfully extracted content from {url}")
            return content_data

        except requests.RequestException as e:
            self.logger.error(f"Error fetching content from {url}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {str(e)}")
            raise

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return ''

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract the main text content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to find main content containers common in Docusaurus
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='main-wrapper') or soup

        # Get text content
        text = main_content.get_text(separator=' ', strip=True)
        return text

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headings with their levels."""
        headings = []
        for i in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', '')
                })
        return headings

    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract code blocks."""
        code_blocks = []
        # Look for common code block selectors in Docusaurus
        code_elements = soup.find_all(['code', 'pre']) or soup.find_all(class_='codeBlock')
        for code_elem in code_elements:
            code_text = code_elem.get_text().strip()
            if code_text:
                code_blocks.append({
                    'language': code_elem.get('class', []),
                    'content': code_text
                })
        return code_blocks

    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """Extract lists (ordered and unordered)."""
        lists = []
        for list_elem in soup.find_all(['ul', 'ol']):
            list_type = 'ordered' if list_elem.name == 'ol' else 'unordered'
            items = [li.get_text().strip() for li in list_elem.find_all('li')]
            lists.append({
                'type': list_type,
                'items': items
            })
        return lists

    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """Extract tables."""
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                row = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                if row:
                    rows.append(row)
            if rows:
                tables.append({
                    'rows': rows
                })
        return tables

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from the page."""
        metadata = {}

        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content

        # Extract other common metadata
        if soup.find('time'):
            metadata['date'] = soup.find('time').get('datetime') or soup.find('time').get_text()

        return metadata

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from the page."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append({
                'text': link.get_text().strip(),
                'url': absolute_url
            })
        return links

    def detect_docusaurus_structure(self, url: str) -> bool:
        """
        Detect if the URL is a Docusaurus site by checking for common indicators.

        Args:
            url: The URL to check

        Returns:
            True if likely a Docusaurus site, False otherwise
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check for common Docusaurus indicators
            indicators = [
                soup.find('meta', {'name': 'generator'}, string=lambda x: x and 'Docusaurus' in x),
                soup.find(class_='navbar'),
                soup.find(class_='theme-doc-sidebar-container'),
                soup.find(class_='doc-page'),
                soup.find(class_='docs-page'),
                soup.find(string=lambda text: text and 'Docusaurus' in text)
            ]

            return any(indicators)

        except Exception:
            # If we can't determine, assume it's not a Docusaurus site
            return False