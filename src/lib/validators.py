"""
Validation and sanitization functions for the embedding pipeline.

This module provides URL validation and sanitization functions for Docusaurus sites
and other validation utilities used throughout the pipeline.
"""
from urllib.parse import urlparse, urljoin
import re
from typing import List, Optional


def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_docusaurus_url(url: str) -> bool:
    """
    Check if a URL appears to be a Docusaurus site based on common patterns.

    Args:
        url: URL to check

    Returns:
        True if likely a Docusaurus URL, False otherwise
    """
    if not is_valid_url(url):
        return False

    try:
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Check for common Docusaurus patterns in the URL
        docusaurus_indicators = [
            '/docs',
            '/category/',
            '/tag/',
            # Common Docusaurus site structures
        ]

        return any(indicator in path for indicator in docusaurus_indicators)

    except Exception:
        return False


def sanitize_url(url: str) -> Optional[str]:
    """
    Sanitize a URL by normalizing it and removing potentially harmful components.

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL or None if invalid
    """
    if not url:
        return None

    # Basic sanitization: strip whitespace
    url = url.strip()

    if not is_valid_url(url):
        return None

    try:
        parsed = urlparse(url)

        # Ensure scheme is http or https
        if parsed.scheme not in ['http', 'https']:
            return None

        # Remove fragments (fragments after #)
        sanitized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            sanitized += f"?{parsed.query}"

        return sanitized

    except Exception:
        return None


def validate_and_sanitize_urls(urls: List[str], allowed_domains: Optional[List[str]] = None) -> List[str]:
    """
    Validate and sanitize a list of URLs, optionally restricting to allowed domains.

    Args:
        urls: List of URLs to validate and sanitize
        allowed_domains: Optional list of allowed domains

    Returns:
        List of validated and sanitized URLs
    """
    valid_urls = []

    for url in urls:
        sanitized = sanitize_url(url)
        if not sanitized:
            continue

        if allowed_domains:
            parsed = urlparse(sanitized)
            if parsed.netloc not in allowed_domains:
                continue

        valid_urls.append(sanitized)

    # Remove duplicates while preserving order
    unique_urls = list(dict.fromkeys(valid_urls))
    return unique_urls


def is_safe_url(url: str, allowed_schemes: Optional[List[str]] = None,
                blocked_patterns: Optional[List[str]] = None) -> bool:
    """
    Check if a URL is safe to access based on schemes and patterns.

    Args:
        url: URL to check
        allowed_schemes: List of allowed schemes (defaults to ['http', 'https'])
        blocked_patterns: List of regex patterns to block

    Returns:
        True if safe, False otherwise
    """
    if not is_valid_url(url):
        return False

    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']

    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in allowed_schemes:
            return False

        # Check for blocked patterns
        if blocked_patterns:
            full_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            for pattern in blocked_patterns:
                if re.search(pattern, full_url, re.IGNORECASE):
                    return False

        return True

    except Exception:
        return False


def extract_urls_from_content(content: str, base_url: str) -> List[str]:
    """
    Extract URLs from content text, resolving relative URLs against a base URL.

    Args:
        content: Content text to extract URLs from
        base_url: Base URL to resolve relative URLs

    Returns:
        List of extracted URLs
    """
    if not content or not base_url:
        return []

    # Regular expression to find URLs in text
    url_pattern = r'https?://[^\s\'"<>]+|www\.[^\s\'"<>]+'
    potential_urls = re.findall(url_pattern, content)

    # Add http:// prefix to www. URLs
    full_urls = []
    for url in potential_urls:
        if url.startswith('www.'):
            full_urls.append(f'http://{url}')
        else:
            full_urls.append(url)

    # Resolve relative URLs and validate
    valid_urls = []
    for url in full_urls:
        try:
            # Join with base URL to handle relative URLs
            full_url = urljoin(base_url, url)
            if is_safe_url(full_url):
                valid_urls.append(full_url)
        except Exception:
            continue

    return validate_and_sanitize_urls(valid_urls)


def normalize_url(url: str) -> str:
    """
    Normalize a URL by standardizing its format.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL
    """
    if not url:
        return ""

    # Parse the URL
    parsed = urlparse(url)

    # Normalize the scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Remove trailing slashes from path
    path = parsed.path.rstrip('/')

    # Reconstruct the URL
    normalized = f"{scheme}://{netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    if parsed.fragment:
        normalized += f"#{parsed.fragment}"

    return normalized


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        True if same domain, False otherwise
    """
    try:
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2
    except Exception:
        return False