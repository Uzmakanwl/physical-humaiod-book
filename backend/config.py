"""
Configuration module for the embedding pipeline.

This module handles configuration for API keys, service endpoints,
and other settings required by the pipeline components.
"""

import os
from typing import Optional


class Config:
    """Configuration class for the embedding pipeline."""

    # Cohere API Configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")

    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY", None)
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "embeddings")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "pipeline.log")

    # Processing Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30"))

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration values are present."""
        if not cls.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        return True