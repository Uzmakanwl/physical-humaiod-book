"""
Logging module for the embedding pipeline.

This module provides logging infrastructure for pipeline operations,
including setup for console and file logging with appropriate levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from config import Config


def setup_logging(log_file: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for the pipeline.

    Args:
        log_file: Path to the log file. If None, uses Config.LOG_FILE
        log_level: Logging level. If None, uses Config.LOG_LEVEL

    Returns:
        Configured logger instance
    """
    # Use config values if not provided
    log_file = log_file or Config.LOG_FILE
    log_level = log_level or Config.LOG_LEVEL

    # Create logger
    logger = logging.getLogger('embedding_pipeline')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Prevent adding handlers multiple times
    if logger.handlers:
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_path = Path(log_file)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name or the default pipeline logger.

    Args:
        name: Name for the logger. If None, returns the default pipeline logger

    Returns:
        Logger instance
    """
    logger_name = name or 'embedding_pipeline'
    return logging.getLogger(logger_name)


# Default logger for the pipeline
logger = setup_logging()