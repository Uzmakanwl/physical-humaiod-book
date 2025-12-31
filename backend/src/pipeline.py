"""
Pipeline manager module for the embedding pipeline.

This module orchestrates the complete workflow of content extraction,
embedding generation, and vector storage with monitoring and error handling.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.extractor import ContentExtractor
from src.validator import ContentValidator, ValidationResult
from src.embedder import EmbeddingGenerator
from src.storage import VectorStorage
from src.utils import retry_on_failure
from config import Config
from src.logger import get_logger


class PipelineManager:
    """Manages the complete embedding pipeline workflow."""

    def __init__(self):
        """Initialize the PipelineManager with all required components."""
        self.extractor = ContentExtractor()
        self.validator = ContentValidator()
        self.embedder = EmbeddingGenerator()
        self.storage = VectorStorage()
        self.logger = get_logger(__name__)

        # Validate configuration on initialization
        self._validate_configuration()

        # Pipeline state tracking
        self.processing_stats = {
            'total_processed': 0,
            'total_errors': 0,
            'start_time': None,
            'end_time': None,
            'urls_processed': [],
            'error_urls': [],
            'processing_times': []
        }

    def process_single_url(self, url: str, validate_content: bool = True) -> Dict[str, Any]:
        """
        Process a single URL through the complete pipeline.

        Args:
            url: The URL to process
            validate_content: Whether to validate content quality before processing

        Returns:
            Dictionary containing processing results
        """
        result = {
            'url': url,
            'status': 'success',
            'errors': [],
            'extracted_content': None,
            'embedding_id': None,
            'processing_time': 0
        }

        start_time = time.time()

        try:
            # Validate URL before extraction
            url_validation = self.validator.validate_before_extraction(url)
            if not url_validation.is_valid:
                result['status'] = 'failed'
                result['errors'].extend(url_validation.errors)
                self.logger.error(f"URL validation failed for {url}: {url_validation.errors}")
                return result

            # Extract content
            self.logger.info(f"Extracting content from {url}")
            extracted_content = self.extractor.extract_content(url)
            result['extracted_content'] = extracted_content

            # Validate content quality if requested
            if validate_content:
                content_validation = self.validator.validate_content(extracted_content)
                if not content_validation.is_valid:
                    result['status'] = 'failed'
                    result['errors'].extend(content_validation.errors)
                    self.logger.error(f"Content validation failed for {url}: {content_validation.errors}")
                    return result

            # Generate embedding
            self.logger.info(f"Generating embedding for {url}")
            text_to_embed = extracted_content.get('text_content', '')[:10000]  # Limit text length
            embedding = self.embedder.generate_embedding(text_to_embed)

            # Validate embedding quality
            embedding_validation = self.embedder.validate_embedding_quality(embedding, text_to_embed)
            if not embedding_validation['is_valid']:
                result['status'] = 'failed'
                result['errors'].append(f"Embedding validation failed: {embedding_validation['issues']}")
                self.logger.error(f"Embedding validation failed for {url}: {embedding_validation['issues']}")
                return result

            # Prepare metadata for storage
            metadata = {
                'source_url': url,
                'title': extracted_content.get('title', ''),
                'extracted_at': datetime.utcnow().isoformat(),
                'content_length': len(text_to_embed),
                'quality_score': content_validation.quality_score if validate_content else 1.0
            }

            # Store embedding
            self.logger.info(f"Storing embedding for {url}")
            embedding_id = self.storage.store_embedding(
                embedding=embedding,
                metadata=metadata,
                text_content=text_to_embed
            )
            result['embedding_id'] = embedding_id

            self.logger.info(f"Successfully processed {url}")

        except Exception as e:
            result['status'] = 'failed'
            error_msg = str(e)
            result['errors'].append(error_msg)

            # Categorize and handle different types of errors
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                self.logger.warning(f"Network error processing {url}: {error_msg}")
            elif "api" in error_msg.lower() or "quota" in error_msg.lower():
                self.logger.error(f"API/service error processing {url}: {error_msg}")
            else:
                self.logger.error(f"Processing error for {url}: {error_msg}")

            self.processing_stats['total_errors'] += 1

        finally:
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time

            # Update statistics
            if result['status'] == 'success':
                self.processing_stats['urls_processed'].append(url)
            else:
                self.processing_stats['error_urls'].append(url)

            self.processing_stats['processing_times'].append(processing_time)

        return result

    def process_multiple_urls(self, urls: List[str], max_workers: int = 4,
                           validate_content: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple URLs through the pipeline concurrently.

        Args:
            urls: List of URLs to process
            max_workers: Maximum number of concurrent workers
            validate_content: Whether to validate content quality before processing

        Returns:
            List of processing results for each URL
        """
        self.logger.info(f"Starting processing of {len(urls)} URLs with {max_workers} workers")
        self.processing_stats['start_time'] = time.time()
        self.processing_stats['total_processed'] = 0
        self.processing_stats['total_errors'] = 0

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.process_single_url, url, validate_content): url
                for url in urls
            }

            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.processing_stats['total_processed'] += 1

                    if result['status'] == 'failed':
                        self.processing_stats['total_errors'] += 1
                        self.logger.warning(f"Failed to process {url}: {result['errors']}")
                    else:
                        self.logger.info(f"Successfully processed {url}")

                except Exception as e:
                    self.logger.error(f"Unexpected error processing {url}: {str(e)}")
                    self.processing_stats['total_errors'] += 1
                    results.append({
                        'url': url,
                        'status': 'failed',
                        'errors': [str(e)],
                        'extracted_content': None,
                        'embedding_id': None,
                        'processing_time': 0
                    })

        self.processing_stats['end_time'] = time.time()
        self._log_processing_summary()

        return results

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Get detailed monitoring statistics for the pipeline.

        Returns:
            Dictionary containing detailed monitoring statistics
        """
        import statistics

        stats = self.get_pipeline_status()
        pipeline_stats = stats['processing_stats']

        # Calculate additional metrics
        if pipeline_stats['processing_times']:
            avg_processing_time = statistics.mean(pipeline_stats['processing_times'])
            median_processing_time = statistics.median(pipeline_stats['processing_times'])
            max_processing_time = max(pipeline_stats['processing_times'])
            min_processing_time = min(pipeline_stats['processing_times'])
        else:
            avg_processing_time = median_processing_time = max_processing_time = min_processing_time = 0

        success_count = len(pipeline_stats['urls_processed'])
        total_count = len(pipeline_stats['urls_processed']) + len(pipeline_stats['error_urls'])
        success_rate = success_count / total_count if total_count > 0 else 0

        detailed_stats = {
            **pipeline_stats,
            'success_rate': success_rate,
            'average_processing_time': avg_processing_time,
            'median_processing_time': median_processing_time,
            'max_processing_time': max_processing_time,
            'min_processing_time': min_processing_time,
            'total_processing_time': sum(pipeline_stats['processing_times']),
            'urls_in_current_session': pipeline_stats['urls_processed'][-10:] if pipeline_stats['urls_processed'] else []  # Last 10 URLs
        }

        return detailed_stats

    def reset_monitoring_stats(self):
        """Reset all monitoring statistics."""
        self.processing_stats = {
            'total_processed': 0,
            'total_errors': 0,
            'start_time': None,
            'end_time': None,
            'urls_processed': [],
            'error_urls': [],
            'processing_times': []
        }

    @retry_on_failure(max_retries=Config.MAX_RETRIES)
    def process_with_retry(self, url: str, validate_content: bool = True) -> Dict[str, Any]:
        """
        Process a URL with automatic retry on failure.

        Args:
            url: The URL to process
            validate_content: Whether to validate content quality before processing

        Returns:
            Dictionary containing processing results
        """
        return self.process_single_url(url, validate_content)

    def search_similar_content(self, query_text: str, limit: int = 10,
                             metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for content similar to the query text.

        Args:
            query_text: Text to find similar content for
            limit: Maximum number of results to return
            metadata_filter: Optional filter for metadata fields

        Returns:
            List of similar content items
        """
        try:
            # Generate embedding for query
            query_embedding = self.embedder.generate_embedding(query_text)

            # Search in vector storage
            results = self.storage.search_similar(
                query_embedding=query_embedding,
                limit=limit,
                metadata_filter=metadata_filter
            )

            self.logger.info(f"Found {len(results)} similar content items for query")
            return results

        except Exception as e:
            self.logger.error(f"Error searching for similar content: {str(e)}")
            raise

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current status of the pipeline."""
        return {
            'processing_stats': self.processing_stats.copy(),
            'components_status': {
                'extractor': 'ready',
                'validator': 'ready',
                'embedder': 'ready',
                'storage': 'ready'
            },
            'collection_info': self.storage.get_collection_info()
        }

    def _log_processing_summary(self):
        """Log a summary of the processing run."""
        if self.processing_stats['start_time'] and self.processing_stats['end_time']:
            total_time = self.processing_stats['end_time'] - self.processing_stats['start_time']
            success_count = self.processing_stats['total_processed'] - self.processing_stats['total_errors']

            self.logger.info(
                f"Processing completed: {success_count}/{self.processing_stats['total_processed']} "
                f"successful in {total_time:.2f}s. Errors: {self.processing_stats['total_errors']}"
            )

    def update_content(self, url: str, force_update: bool = False) -> Dict[str, Any]:
        """
        Update content for an existing URL (if changed).

        Args:
            url: The URL to update
            force_update: Whether to force update regardless of changes

        Returns:
            Dictionary containing update results
        """
        # Check if content has been updated by comparing with stored version
        # This is a simplified implementation - in a real system you might use ETags,
        # last-modified headers, or content checksums
        self.logger.info(f"Checking for updates for {url}")

        # First, try to retrieve any existing embedding for this URL
        existing_embedding_id = None
        # In a real implementation, you would search for embeddings with this URL in metadata
        # For now, we'll just reprocess if force_update is True or proceed with processing

        if force_update:
            self.logger.info(f"Force update requested for {url}")
            return self.process_single_url(url)
        else:
            # In a full implementation, you would:
            # 1. Search for existing embeddings with this URL
            # 2. Fetch the original content and compare with current content
            # 3. Only update if content has changed
            self.logger.info(f"Performing update check for {url}")
            return self.process_single_url(url)

    def has_content_changed(self, url: str, current_content: str) -> bool:
        """
        Check if content has changed since last processing.

        Args:
            url: The URL to check
            current_content: The current content to compare

        Returns:
            True if content has changed, False otherwise
        """
        # In a real implementation, you would:
        # 1. Retrieve the previously stored content or a hash/checksum
        # 2. Compare it with the current content
        # 3. Return True if different, False otherwise

        # For now, we'll return True to indicate content has changed
        # This would trigger an update in the update_content method
        self.logger.debug(f"Content change detection for {url}")
        return True  # Simplified implementation - assumes content always changes

    def _validate_configuration(self):
        """Validate pipeline configuration on initialization."""
        from config import Config

        # Validate required configuration values
        if not Config.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY must be set in environment variables")

        # Log configuration for debugging (without exposing sensitive keys)
        self.logger.info("Pipeline configuration validated successfully")
        self.logger.info(f"Qdrant host: {Config.QDRANT_HOST}:{Config.QDRANT_PORT}")
        self.logger.info(f"Collection name: {Config.COLLECTION_NAME}")
        self.logger.info(f"Batch size: {Config.BATCH_SIZE}")
        self.logger.info(f"Max retries: {Config.MAX_RETRIES}")
        self.logger.info(f"Timeout: {Config.TIMEOUT}")

    def validate_pipeline_health(self) -> Dict[str, Any]:
        """
        Validate the health of all pipeline components.

        Returns:
            Dictionary with health status of each component
        """
        health_status = {
            'extractor': True,
            'validator': True,
            'embedder': True,
            'storage': True,
            'overall': True,
            'issues': []
        }

        # Test extractor
        try:
            # The extractor doesn't need specific health checks since it's just HTTP requests
            pass
        except Exception as e:
            health_status['extractor'] = False
            health_status['overall'] = False
            health_status['issues'].append(f"Extractor issue: {str(e)}")

        # Test validator
        try:
            from src.validator import ContentValidator
            validator = ContentValidator()
            # Test validation with simple content
            test_content = {'url': 'https://test.com', 'text_content': 'test'}
            validator.validate_content(test_content)
        except Exception as e:
            health_status['validator'] = False
            health_status['overall'] = False
            health_status['issues'].append(f"Validator issue: {str(e)}")

        # Test embedder
        try:
            # The embedder uses external API, so we can't easily test without a valid API key
            # Just check that it initializes properly
            from src.embedder import EmbeddingGenerator
            from config import Config
            if not Config.COHERE_API_KEY:
                health_status['embedder'] = False
                health_status['overall'] = False
                health_status['issues'].append("Embedder: COHERE_API_KEY not configured")
        except Exception as e:
            health_status['embedder'] = False
            health_status['overall'] = False
            health_status['issues'].append(f"Embedder issue: {str(e)}")

        # Test storage
        try:
            # Test storage by attempting to get collection info
            collection_info = self.storage.get_collection_info()
            # If we get here without exception, storage is accessible
        except Exception as e:
            health_status['storage'] = False
            health_status['overall'] = False
            health_status['issues'].append(f"Storage issue: {str(e)}")

        return health_status

    def schedule_processing(self, urls: List[str], interval_hours: int = 24,
                          validate_content: bool = True) -> threading.Thread:
        """
        Schedule periodic processing of URLs.

        Args:
            urls: List of URLs to process periodically
            interval_hours: Interval between processing runs in hours
            validate_content: Whether to validate content quality before processing

        Returns:
            Thread object for the scheduling task
        """
        def schedule_worker():
            while True:
                self.logger.info(f"Starting scheduled processing run for {len(urls)} URLs")
                results = self.process_multiple_urls(urls, validate_content=validate_content)

                # Count successful updates
                successful = sum(1 for r in results if r['status'] == 'success')
                self.logger.info(f"Scheduled run completed: {successful}/{len(urls)} successful")

                # Wait for the interval
                time.sleep(interval_hours * 3600)

        # Start the scheduling thread
        scheduler_thread = threading.Thread(target=schedule_worker, daemon=True)
        scheduler_thread.start()

        self.logger.info(f"Scheduled processing for {len(urls)} URLs every {interval_hours} hours")
        return scheduler_thread