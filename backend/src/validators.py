"""
Validation functions for the embedding pipeline.

This module contains functions for validating URLs, content,
and other inputs to ensure security and correctness.
"""

import re
from urllib.parse import urlparse
from typing import Union, List
import requests
from src.logger import get_logger


def validate_url(url: str) -> bool:
    """
    Validate a URL format and basic structure.

    Args:
        url: The URL to validate

    Returns:
        True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        # Check if the URL has a valid scheme and netloc
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def is_safe_url(url: str, allowed_domains: Union[List[str], None] = None) -> bool:
    """
    Check if a URL is safe to access (prevents SSRF and similar attacks).

    Args:
        url: The URL to check
        allowed_domains: List of allowed domains (if None, all domains are allowed)

    Returns:
        True if the URL is safe, False otherwise
    """
    try:
        parsed = urlparse(url)

        # Basic validation
        if not all([parsed.scheme, parsed.netloc]):
            return False

        if parsed.scheme not in ['http', 'https']:
            return False

        # Check for suspicious components
        if parsed.netloc.startswith(('127.', '10.', '192.168.', '172.')) and not _is_private_allowed():
            # Potential internal IP access - could be SSRF
            return False

        if re.search(r'localhost|loopback', parsed.netloc, re.IGNORECASE):
            return False

        # If allowed domains are specified, check against them
        if allowed_domains:
            return any(domain in parsed.netloc for domain in allowed_domains)

        return True
    except Exception:
        return False


def _is_private_allowed() -> bool:
    """
    Internal function to determine if private IP access should be allowed.
    This could be configured via environment variables or config.
    """
    # For now, always return False to prevent SSRF
    # In a real implementation, this might check a config setting
    return False


def validate_content_type(content_type: str) -> bool:
    """
    Validate if a content type is allowed for processing.

    Args:
        content_type: The content type to validate

    Returns:
        True if the content type is allowed, False otherwise
    """
    allowed_types = [
        'text/html',
        'application/xhtml+xml',
        'text/plain',
        'application/json'  # For API responses that might contain documentation
    ]

    # Extract the main content type (before any parameters)
    main_type = content_type.split(';')[0].strip().lower()

    return main_type in allowed_types


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize input text to prevent injection attacks.

    Args:
        text: The text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes
    text = text.replace('\x00', '')

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    # Remove potentially dangerous characters/sequences
    # This is a basic sanitization - in a real implementation,
    # you might want more thorough cleaning
    dangerous_patterns = [
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'vbscript:',  # VBScript URLs
        r'on\w+\s*=',  # Event handlers
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()


def validate_docusaurus_url(url: str) -> bool:
    """
    Validate if a URL appears to be a Docusaurus site.

    Args:
        url: The URL to validate

    Returns:
        True if the URL appears to be a Docusaurus site, False otherwise
    """
    try:
        # First validate the URL format
        if not validate_url(url):
            return False

        # For a more thorough check, we could make a request to the URL
        # and look for Docusaurus-specific elements, but that's more expensive
        # For now, we'll just check the format
        return True

    except Exception:
        return False


def validate_batch_urls(urls: List[str]) -> dict:
    """
    Validate a batch of URLs and return validation results.

    Args:
        urls: List of URLs to validate

    Returns:
        Dictionary with validation results
    """
    results = {
        'valid_urls': [],
        'invalid_urls': [],
        'safe_urls': [],
        'unsafe_urls': [],
        'total_urls': len(urls)
    }

    logger = get_logger(__name__)

    for url in urls:
        # Validate format
        if validate_url(url):
            results['valid_urls'].append(url)
        else:
            results['invalid_urls'].append(url)
            continue  # If URL is invalid, don't check if it's safe

        # Validate safety
        if is_safe_url(url):
            results['safe_urls'].append(url)
        else:
            results['unsafe_urls'].append(url)

    logger.info(
        f"URL validation completed: {len(results['valid_urls'])}/{results['total_urls']} valid, "
        f"{len(results['safe_urls'])}/{results['total_urls']} safe"
    )

    return results


def check_url_accessibility(url: str, timeout: int = 10) -> dict:
    """
    Check if a URL is accessible and return status information.

    Args:
        url: The URL to check
        timeout: Request timeout in seconds

    Returns:
        Dictionary with accessibility information
    """
    if not validate_url(url):
        return {
            'accessible': False,
            'status_code': None,
            'error': 'Invalid URL format',
            'content_type': None
        }

    if not is_safe_url(url):
        return {
            'accessible': False,
            'status_code': None,
            'error': 'URL is not safe to access',
            'content_type': None
        }

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)

        return {
            'accessible': response.status_code < 400,
            'status_code': response.status_code,
            'error': None if response.status_code < 400 else f"HTTP {response.status_code}",
            'content_type': response.headers.get('content-type', '')
        }
    except requests.exceptions.RequestException as e:
        return {
            'accessible': False,
            'status_code': None,
            'error': str(e),
            'content_type': None
        }
    except Exception as e:
        return {
            'accessible': False,
            'status_code': None,
            'error': f"Unexpected error: {str(e)}",
            'content_type': None
        }


def validate_text_content(text: str, min_length: int = 10, max_length: int = 50000) -> dict:
    """
    Validate extracted text content.

    Args:
        text: The text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        Dictionary with validation results
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'length': len(text) if text else 0
    }

    if text is None:
        result['is_valid'] = False
        result['errors'].append('Text is None')
        return result

    # Check length
    text_len = len(text)
    if text_len < min_length:
        result['is_valid'] = False
        result['errors'].append(f'Text too short: {text_len} characters (minimum: {min_length})')

    if text_len > max_length:
        result['is_valid'] = False
        result['errors'].append(f'Text too long: {text_len} characters (maximum: {max_length})')

    # Check for potentially problematic content
    if text_len > 0 and len(text.strip()) == 0:
        result['warnings'].append('Text contains only whitespace')

    # Check for excessive repetition (potential scraping issue)
    if text_len > 100:
        # Check if more than 50% of the text is repeated patterns
        sample_size = min(50, text_len // 4)
        if sample_size > 0:
            sample = text[:sample_size]
            if sample in text[sample_size:]:
                repeated_count = text.count(sample)
                if repeated_count > text_len // (sample_size * 2):
                    result['warnings'].append('Text contains repeated patterns - may be scraped content')

    return result


def validate_metadata(metadata: dict) -> dict:
    """
    Validate metadata for storage.

    Args:
        metadata: The metadata to validate

    Returns:
        Dictionary with validation results
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    if not isinstance(metadata, dict):
        result['is_valid'] = False
        result['errors'].append('Metadata must be a dictionary')
        return result

    # Check for problematic keys or values
    for key, value in metadata.items():
        if not isinstance(key, str):
            result['errors'].append(f'Metadata key must be string: {type(key)}')
            continue

        # Check key length
        if len(key) > 100:
            result['warnings'].append(f'Metadata key too long: {key[:50]}...')

        # Check value types that might not be JSON serializable
        if isinstance(value, (set, frozenset)):
            result['errors'].append(f'Metadata value for key "{key}" is not JSON serializable: {type(value)}')

    return result