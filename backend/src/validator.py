"""
Content validator module for the embedding pipeline.

This module handles validation of extracted content for quality,
completeness, and suitability for embedding generation.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

from src.logger import get_logger


@dataclass
class ValidationResult:
    """Result of content validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float


class ContentValidator:
    """Validates extracted content for quality and suitability."""

    def __init__(self):
        """Initialize the ContentValidator."""
        self.logger = get_logger(__name__)

    def validate_content(self, content_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate extracted content.

        Args:
            content_data: Dictionary containing extracted content data

        Returns:
            ValidationResult with validation results
        """
        errors = []
        warnings = []

        # Check for required fields
        required_fields = ['url', 'text_content']
        for field in required_fields:
            if field not in content_data or not content_data[field]:
                errors.append(f"Missing required field: {field}")

        if errors:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                quality_score=0.0
            )

        # Validate URL format
        url_validation = self._validate_url(content_data['url'])
        if not url_validation:
            errors.append(f"Invalid URL format: {content_data['url']}")

        # Check content quality
        content_quality = self._assess_content_quality(content_data)
        quality_score = content_quality['score']

        # Add any quality issues as warnings
        warnings.extend(content_quality['warnings'])

        # Check if content meets minimum requirements
        if quality_score < 0.3:
            errors.append(f"Content quality too low (score: {quality_score})")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score
        )

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _assess_content_quality(self, content_data: Dict[str, Any]) -> Dict[str, any]:
        """Assess the quality of extracted content."""
        text_content = content_data.get('text_content', '')
        title = content_data.get('title', '')
        headings = content_data.get('headings', [])
        code_blocks = content_data.get('code_blocks', [])
        metadata = content_data.get('metadata', {})

        score = 1.0  # Start with perfect score
        warnings = []

        # Check text content length
        if len(text_content.strip()) < 50:
            score -= 0.3
            warnings.append("Content is very short (< 50 characters)")

        # Check for meaningful content
        if not text_content.strip() or text_content.count(' ') < 5:
            score -= 0.4
            warnings.append("Content appears to have minimal text")

        # Check title quality
        if not title.strip():
            score -= 0.1
            warnings.append("No title found")

        # Check heading structure
        if len(headings) < 1:
            score -= 0.1
            warnings.append("No headings found - content may lack structure")

        # Check for metadata
        if not metadata:
            score -= 0.1
            warnings.append("No metadata found")

        # Check for code blocks
        if len(code_blocks) > 0:
            # Code blocks can add value to content
            score += 0.1
            # Cap the bonus
            score = min(score, 1.0)

        # Apply minimum score
        score = max(score, 0.0)

        return {
            'score': score,
            'warnings': warnings
        }

    def validate_before_extraction(self, url: str) -> ValidationResult:
        """
        Validate a URL before content extraction.

        Args:
            url: The URL to validate

        Returns:
            ValidationResult with validation results
        """
        errors = []
        warnings = []

        # Validate URL format
        if not self._validate_url(url):
            errors.append(f"Invalid URL format: {url}")
        else:
            # Additional URL checks
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                errors.append(f"Invalid URL scheme: {parsed.scheme}")

        # Check for potentially problematic patterns
        if re.search(r'login|signin|signup|register', url, re.IGNORECASE):
            warnings.append("URL may be a login/signin page, content might not be suitable")

        if re.search(r'\.(pdf|doc|docx|xls|xlsx|zip|rar|exe|dmg)$', url):
            errors.append("URL points to a file, not a web page")

        is_valid = len(errors) == 0
        quality_score = 0.0 if not is_valid else 1.0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score
        )