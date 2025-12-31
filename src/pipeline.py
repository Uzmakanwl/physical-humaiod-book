"""
Pipeline manager module for workflow orchestration.

This module provides functionality to orchestrate the complete embedding pipeline,
including content extraction, validation, embedding generation, and storage,
with monitoring, error handling, and configurable scheduling.
"""
import asyncio
from typing import List, Dict, Optional, Any
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.models.models import ProcessingResult, PipelineConfig


@dataclass
class PipelineStep:
    """Represents a step in the pipeline."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"  # running, completed, failed
    error: Optional[str] = None


class PipelineManager:
    """Pipeline manager for workflow orchestration."""

    def __init__(self, config: PipelineConfig):
        """
        Initialize the pipeline manager.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # Initialize components (will be set by the user)
        self.extractor = None
        self.validator = None
        self.embedder = None
        self.storage = None

        # Track pipeline execution
        self.current_steps: List[PipelineStep] = []
        self.completed_steps: List[PipelineStep] = []

    def setup_logging(self):
        """Set up logging based on configuration."""
        logging.basicConfig(
            level=self.config.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )

    def set_components(self, extractor, validator, embedder, storage):
        """
        Set the pipeline components.

        Args:
            extractor: ContentExtractor instance
            validator: ContentValidator instance
            embedder: EmbeddingGenerator instance
            storage: VectorStorage instance
        """
        self.extractor = extractor
        self.validator = validator
        self.embedder = embedder
        self.storage = storage

    async def process_url(self, url: str) -> ProcessingResult:
        """
        Process a single URL through the complete pipeline.

        Args:
            url: URL to process

        Returns:
            ProcessingResult indicating the outcome
        """
        start_time = time.time()
        errors = []

        try:
            self.logger.info(f"Starting processing for URL: {url}")

            # Step 1: Extract content
            extraction_step = self._start_step("content_extraction")
            try:
                extraction_result = self.extractor.extract_from_url(url)
                if not extraction_result:
                    raise Exception("Content extraction failed")
                self._complete_step(extraction_step)
            except Exception as e:
                self._fail_step(extraction_step, str(e))
                errors.append(f"Content extraction failed: {str(e)}")
                return ProcessingResult(
                    url=url,
                    status="failed",
                    errors=errors,
                    processing_time=time.time() - start_time
                )

            # Step 2: Validate content
            validation_step = self._start_step("content_validation")
            try:
                validation_result = self.validator.validate_url_content(extraction_result)
                if not validation_result.is_valid:
                    self.logger.warning(f"Content validation failed for {url} with score {validation_result.quality_score}")
                    # Continue processing even if validation fails, but log the issue
                self._complete_step(validation_step)
            except Exception as e:
                self._fail_step(validation_step, str(e))
                errors.append(f"Content validation failed: {str(e)}")

            # Step 3: Generate embeddings
            embedding_step = self._start_step("embedding_generation")
            try:
                # Split content into chunks if it's too long
                text_chunks = self._chunk_text(extraction_result.text_content)
                embeddings_result = self.embedder.generate_embeddings(text_chunks)

                # Validate embedding consistency
                if not self.embedder.validate_embedding_consistency(embeddings_result):
                    self.logger.warning(f"Embedding consistency validation failed for {url}")

                self._complete_step(embedding_step)
            except Exception as e:
                self._fail_step(embedding_step, str(e))
                errors.append(f"Embedding generation failed: {str(e)}")
                return ProcessingResult(
                    url=url,
                    status="failed",
                    errors=errors,
                    processing_time=time.time() - start_time
                )

            # Step 4: Store embeddings
            storage_step = self._start_step("embedding_storage")
            try:
                texts = [chunk for chunk in text_chunks]
                embeddings = [result.embedding for result in embeddings_result if result.is_valid]

                if len(texts) != len(embeddings):
                    # Filter out invalid embeddings
                    valid_pairs = [(text, emb) for text, emb in zip(texts, embeddings) if emb]
                    if valid_pairs:
                        texts, embeddings = zip(*valid_pairs)
                        texts, embeddings = list(texts), list(embeddings)
                    else:
                        raise Exception("No valid embeddings to store")

                # Prepare metadata for each chunk
                metadata_list = []
                for i, chunk in enumerate(text_chunks):
                    metadata = {
                        "source_url": url,
                        "chunk_index": i,
                        "total_chunks": len(text_chunks),
                        "original_title": extraction_result.title
                    }
                    metadata_list.append(metadata)

                storage_results = self.storage.batch_store_with_retry(texts, embeddings, metadata_list)
                self._complete_step(storage_step)
            except Exception as e:
                self._fail_step(storage_step, str(e))
                errors.append(f"Embedding storage failed: {str(e)}")
                return ProcessingResult(
                    url=url,
                    status="failed",
                    errors=errors,
                    processing_time=time.time() - start_time
                )

            # Success
            self.logger.info(f"Successfully processed URL: {url}")
            return ProcessingResult(
                url=url,
                status="success",
                errors=[],
                extracted_content=extraction_result,
                embedding_id=storage_results[0].embedding_id if storage_results else None,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            error_msg = f"Pipeline processing failed: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            return ProcessingResult(
                url=url,
                status="failed",
                errors=errors,
                processing_time=time.time() - start_time
            )

    async def process_urls(self, urls: List[str]) -> List[ProcessingResult]:
        """
        Process multiple URLs through the pipeline.

        Args:
            urls: List of URLs to process

        Returns:
            List of ProcessingResult objects
        """
        results = []
        total_urls = len(urls)

        self.logger.info(f"Starting to process {total_urls} URLs")

        for i, url in enumerate(urls):
            self.logger.info(f"Processing URL {i+1}/{total_urls}: {url}")

            result = await self.process_url(url)
            results.append(result)

            # Log progress
            success_count = len([r for r in results if r.status == "success"])
            self.logger.info(f"Progress: {i+1}/{total_urls}, Success: {success_count}, Failed: {len(results) - success_count}")

        return results

    def _start_step(self, step_name: str) -> PipelineStep:
        """Start tracking a pipeline step."""
        step = PipelineStep(name=step_name, start_time=time.time())
        self.current_steps.append(step)
        return step

    def _complete_step(self, step: PipelineStep):
        """Mark a pipeline step as completed."""
        step.end_time = time.time()
        step.status = "completed"
        self.current_steps.remove(step)
        self.completed_steps.append(step)

    def _fail_step(self, step: PipelineStep, error: str):
        """Mark a pipeline step as failed."""
        step.end_time = time.time()
        step.status = "failed"
        step.error = error
        self.current_steps.remove(step)
        self.completed_steps.append(step)

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "current_steps": [step.name for step in self.current_steps],
            "completed_steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "duration": step.end_time - step.start_time if step.end_time else None,
                    "error": step.error
                }
                for step in self.completed_steps
            ],
            "active": len(self.current_steps) > 0
        }

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            start = end - overlap

            # Ensure we don't go beyond the text length
            if start >= len(text):
                break

        return chunks

    def run_pipeline(self, urls: List[str]) -> List[ProcessingResult]:
        """
        Run the complete pipeline synchronously.

        Args:
            urls: List of URLs to process

        Returns:
            List of ProcessingResult objects
        """
        # Create event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.process_urls(urls))

    def schedule_pipeline(self, urls: List[str], interval_minutes: int = 60):
        """
        Schedule the pipeline to run at regular intervals.

        Args:
            urls: List of URLs to process
            interval_minutes: Interval between runs in minutes
        """
        import threading

        def run_scheduled():
            while True:
                try:
                    self.logger.info("Starting scheduled pipeline run")
                    results = self.run_pipeline(urls)

                    success_count = len([r for r in results if r.status == "success"])
                    self.logger.info(f"Scheduled run completed: {success_count}/{len(results)} successful")

                    # Wait for the specified interval
                    time.sleep(interval_minutes * 60)
                except Exception as e:
                    self.logger.error(f"Error in scheduled pipeline: {str(e)}")
                    time.sleep(interval_minutes * 60)  # Wait before retrying

        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=run_scheduled, daemon=True)
        scheduler_thread.start()

        self.logger.info(f"Pipeline scheduled to run every {interval_minutes} minutes")