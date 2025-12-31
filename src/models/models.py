"""
Data models for the embedding pipeline.

This module defines the core data models used throughout the pipeline.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class ContentExtractionResult:
    """Model for content extraction results."""
    url: str
    title: str
    text_content: str
    headings: List[Dict[str, Any]]
    code_blocks: List[Dict[str, str]]
    lists: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    metadata: Dict[str, str]
    links: List[Dict[str, str]]
    extracted_at: datetime = datetime.now()


@dataclass
class EmbeddingResult:
    """Model for embedding generation results."""
    text: str
    embedding: List[float]
    quality_score: float
    is_valid: bool
    generation_time: float
    model_used: str


@dataclass
class StorageResult:
    """Model for storage operation results."""
    embedding_id: str
    stored_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None
    text_content: str = None


@dataclass
class SearchResult:
    """Model for search results."""
    id: str
    score: float
    payload: Dict[str, Any]
    vector: List[float]


@dataclass
class ProcessingResult:
    """Model for overall processing results."""
    url: str
    status: str  # 'success', 'failed'
    errors: List[str]
    extracted_content: Optional[ContentExtractionResult] = None
    embedding_id: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class PipelineConfig:
    """Model for pipeline configuration."""
    cohere_api_key: str
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    collection_name: str = "embeddings"
    batch_size: int = 10
    max_retries: int = 3
    timeout: int = 30
    log_level: str = "INFO"
    log_file: str = "pipeline.log"


@dataclass
class ValidationResult:
    """Model for validation results."""
    is_valid: bool
    quality_score: float
    errors: List[str]
    warnings: List[str]
    validation_time: datetime = datetime.now()


@dataclass
class DocumentStructure:
    """Model for document structure information."""
    title: str
    url: str
    headings: List[Dict[str, Any]]  # Each heading has level, text, id
    content_blocks: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    breadcrumb_path: str