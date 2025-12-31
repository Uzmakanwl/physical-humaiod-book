"""
Utility functions for the embedding pipeline.

This module contains utility functions including error handling,
retry mechanisms, and other helper functions.
"""

import time
import functools
from typing import Callable, Any
from config import Config
from src.logger import get_logger


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry a function on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(__name__)
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {retries}/{max_retries}): {str(e)}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            return func(*args, **kwargs)  # This line should not be reached
        return wrapper
    return decorator


def validate_retry_config():
    """Validate retry configuration values."""
    if Config.MAX_RETRIES < 0:
        raise ValueError("MAX_RETRIES must be non-negative")
    if Config.TIMEOUT <= 0:
        raise ValueError("TIMEOUT must be positive")


class RateLimiter:
    """Simple rate limiter to control API call frequency."""

    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize the rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in the time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.logger = get_logger(__name__)

    def wait_if_needed(self):
        """Wait if the rate limit would be exceeded."""
        current_time = time.time()

        # Remove calls that are outside the time window
        self.calls = [call_time for call_time in self.calls if current_time - call_time <= self.time_window]

        if len(self.calls) >= self.max_calls:
            # Need to wait until the oldest call is outside the window
            sleep_time = self.time_window - (current_time - self.calls[0])
            if sleep_time > 0:
                self.logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                # Remove calls that are now outside the window after sleeping
                current_time = time.time()
                self.calls = [call_time for call_time in self.calls if current_time - call_time <= self.time_window]

        # Add the current call
        self.calls.append(current_time)


def format_bytes(bytes_value: int) -> str:
    """Format bytes value into human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text for processing.

    Args:
        text: Text to sanitize
        max_length: Maximum length of text to return

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes and other problematic characters
    sanitized = text.replace('\x00', '').strip()

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def calculate_similarity_score(embedding1: list, embedding2: list) -> float:
    """
    Calculate cosine similarity between two embeddings.
    This is a simplified version - in practice, you'd use the embedder's method.
    """
    try:
        import numpy as np

        if not embedding1 or not embedding2 or len(embedding1) != len(embedding2):
            return 0.0

        v1 = np.array(embedding1)
        v2 = np.array(embedding2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        similarity = dot_product / (norm_v1 * norm_v2)
        # Ensure similarity is between 0 and 1
        return max(0.0, min(1.0, float(similarity)))
    except ImportError:
        # Fallback if numpy is not available
        return 0.5  # Return neutral similarity if we can't calculate


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks of specified size.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def time_function(func: Callable) -> Callable:
    """
    Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Timed function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(__name__)
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper


def exponential_backoff_retry(max_retries: int = 5, base_delay: float = 1.0):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(__name__)
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e

                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)

            # This should never be reached
            raise last_exception
        return wrapper
    return decorator