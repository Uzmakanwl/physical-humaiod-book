"""
Library module initialization.
"""
from .config import Config, config
from .utils import *
from .validators import *
from .structure import *

__all__ = [
    'Config', 'config',
    'retry_on_failure', 'time_it', 'chunk_list', 'validate_url', 'sanitize_text', 'calculate_similarity_score',
    'is_valid_url', 'is_docusaurus_url', 'sanitize_url', 'validate_and_sanitize_urls', 'is_safe_url',
    'extract_urls_from_content', 'normalize_url', 'is_same_domain',
    'preserve_document_hierarchy', 'create_document_outline', 'extract_content_by_heading_level',
    'preserve_formatting_elements', 'segment_content_by_headings', 'flatten_hierarchy'
]