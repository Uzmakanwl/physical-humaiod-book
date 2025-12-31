"""
Configuration module for the embedding pipeline.

This module handles configuration for API keys, service endpoints,
and other settings required by the pipeline components.
"""
import os
from typing import Optional
from dataclasses import dataclass

from src.models.models import PipelineConfig as PipelineConfigModel


@dataclass
class Config:
    """Configuration class for the embedding pipeline."""

    # Cohere API Configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")

    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY", None)
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL", None)  # For cloud instances
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "embeddings")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "pipeline.log")

    # Processing Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30"))

    # Content Extraction Configuration
    EXTRACTION_TIMEOUT: int = int(os.getenv("EXTRACTION_TIMEOUT", "30"))
    MAX_URLS: int = int(os.getenv("MAX_URLS", "100"))
    ALLOWED_DOMAINS: Optional[str] = os.getenv("ALLOWED_DOMAINS", None)

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration values are present."""
        if not cls.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        return True

    @classmethod
    def get_pipeline_config(cls) -> PipelineConfigModel:
        """Get a PipelineConfig model instance from the configuration."""
        allowed_domains = None
        if cls.ALLOWED_DOMAINS:
            allowed_domains = cls.ALLOWED_DOMAINS.split(',')

        return PipelineConfigModel(
            cohere_api_key=cls.COHERE_API_KEY,
            qdrant_host=cls.QDRANT_HOST,
            qdrant_port=cls.QDRANT_PORT,
            qdrant_api_key=cls.QDRANT_API_KEY,
            collection_name=cls.COLLECTION_NAME,
            batch_size=cls.BATCH_SIZE,
            max_retries=cls.MAX_RETRIES,
            timeout=cls.TIMEOUT,
            log_level=cls.LOG_LEVEL,
            log_file=cls.LOG_FILE
        )


# Create a global config instance
config = Config()