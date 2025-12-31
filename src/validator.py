"""
Content validator module for quality checks.

This module provides functionality to validate extracted content quality,
check for completeness, and ensure content meets the required standards
for embedding generation.
"""
from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass
import logging

from src.models.models import ContentExtractionResult, ValidationResult


@dataclass
class ValidationConfig:
    """Configuration for content validation."""
    min_content_length: int = 50  # Minimum number of characters
    max_content_length: int = 100000  # Maximum number of characters
    min_quality_score: float = 0.5  # Minimum quality score (0.0 to 1.0)
    required_elements: List[str] = None  # Required elements in content
    forbidden_patterns: List[str] = None  # Patterns that indicate poor quality
    min_word_count: int = 10  # Minimum number of words
    max_empty_ratio: float = 0.5  # Maximum ratio of empty content


class ContentValidator:
    """Content validator for quality checks."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Initialize the content validator.

        Args:
            config: Validation configuration (optional)
        """
        self.config = config or ValidationConfig()
        self.logger = logging.getLogger(__name__)

        # Set default required elements if not provided
        if self.config.required_elements is None:
            self.config.required_elements = []

        # Set default forbidden patterns if not provided
        if self.config.forbidden_patterns is None:
            self.config.forbidden_patterns = [
                r'page not found',
                r'error 404',
                r'access denied',
                r'forbidden',
                r'under construction'
            ]

    def validate(self, content: ContentExtractionResult) -> ValidationResult:
        """
        Validate extracted content quality.

        Args:
            content: ContentExtractionResult to validate

        Returns:
            ValidationResult indicating validation status and quality score
        """
        errors = []
        warnings = []

        # Check content length
        length_valid, length_errors = self._validate_content_length(content.text_content)
        errors.extend(length_errors)

        # Check for forbidden patterns
        pattern_valid, pattern_errors = self._validate_forbidden_patterns(content.text_content)
        errors.extend(pattern_errors)

        # Check word count
        word_count_valid, word_errors = self._validate_word_count(content.text_content)
        errors.extend(word_errors)

        # Check for required elements
        required_valid, required_warnings = self._validate_required_elements(content)
        warnings.extend(required_warnings)

        # Calculate quality score based on validation results
        quality_score = self._calculate_quality_score(
            content, length_valid, pattern_valid, word_count_valid
        )

        # Determine if content is valid based on quality score
        is_valid = quality_score >= self.config.min_quality_score

        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            errors=errors,
            warnings=warnings
        )

    def _validate_content_length(self, text: str) -> tuple[bool, List[str]]:
        """
        Validate content length against minimum and maximum requirements.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if len(text) < self.config.min_content_length:
            errors.append(
                f"Content too short: {len(text)} characters, minimum is {self.config.min_content_length}"
            )

        if len(text) > self.config.max_content_length:
            errors.append(
                f"Content too long: {len(text)} characters, maximum is {self.config.max_content_length}"
            )

        return len(errors) == 0, errors

    def _validate_forbidden_patterns(self, text: str) -> tuple[bool, List[str]]:
        """
        Validate content against forbidden patterns.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        text_lower = text.lower()

        for pattern in self.config.forbidden_patterns:
            if re.search(pattern, text_lower):
                errors.append(f"Content contains forbidden pattern: {pattern}")

        return len(errors) == 0, errors

    def _validate_word_count(self, text: str) -> tuple[bool, List[str]]:
        """
        Validate word count against minimum requirement.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Count words using regex
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)

        if word_count < self.config.min_word_count:
            errors.append(
                f"Content has too few words: {word_count}, minimum is {self.config.min_word_count}"
            )

        return len(errors) == 0, errors

    def _validate_required_elements(self, content: ContentExtractionResult) -> tuple[bool, List[str]]:
        """
        Validate that required elements are present in the content.

        Args:
            content: ContentExtractionResult to validate

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        for element in self.config.required_elements:
            if element == 'headings' and not content.headings:
                warnings.append("Content has no headings")
            elif element == 'code_blocks' and not content.code_blocks:
                warnings.append("Content has no code blocks")
            elif element == 'lists' and not content.lists:
                warnings.append("Content has no lists")
            elif element == 'tables' and not content.tables:
                warnings.append("Content has no tables")

        return len(warnings) == 0, warnings

    def _calculate_quality_score(self, content: ContentExtractionResult,
                               length_valid: bool, pattern_valid: bool,
                               word_count_valid: bool) -> float:
        """
        Calculate quality score based on validation results.

        Args:
            content: ContentExtractionResult being validated
            length_valid: Whether content length is valid
            pattern_valid: Whether content passes pattern validation
            word_count_valid: Whether word count is valid

        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0

        # Start with a base score based on text length (longer content generally better)
        if len(content.text_content) > 0:
            # Normalize length to a 0-1 scale (with diminishing returns)
            length_score = min(1.0, len(content.text_content) / 5000.0)
            length_score = min(0.8, length_score)  # Cap at 0.8 to allow for other factors
            score += length_score * 0.3  # Weight 30%

        # Add points for passing validation checks
        if length_valid:
            score += 0.2  # Weight 20%
        if pattern_valid:
            score += 0.2  # Weight 20%
        if word_count_valid:
            score += 0.15  # Weight 15%

        # Add points for rich content elements
        if content.headings:
            score += 0.05  # Weight 5%
        if content.code_blocks:
            score += 0.05  # Weight 5%
        if content.lists or content.tables:
            score += 0.05  # Weight 5%

        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, score))

    def validate_url_content(self, content: ContentExtractionResult) -> ValidationResult:
        """
        Validate content extracted from a URL with additional URL-specific checks.

        Args:
            content: ContentExtractionResult to validate

        Returns:
            ValidationResult indicating validation status and quality score
        """
        # First perform standard validation
        base_validation = self.validate(content)

        errors = base_validation.errors.copy()
        warnings = base_validation.warnings.copy()

        # Additional URL-specific validations
        if not content.url:
            errors.append("Content has no associated URL")

        if not content.title:
            warnings.append("Content has no title")

        # Calculate adjusted quality score based on additional factors
        quality_score = base_validation.quality_score
        if not content.url:
            quality_score *= 0.8  # Reduce score if no URL
        if not content.title:
            quality_score *= 0.9  # Reduce score if no title

        is_valid = quality_score >= self.config.min_quality_score and len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            errors=errors,
            warnings=warnings
        )