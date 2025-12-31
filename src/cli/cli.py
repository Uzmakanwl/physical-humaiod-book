"""
Command Line Interface for the Embedding Pipeline.

This module provides a CLI for running the embedding pipeline with various options.
"""
import argparse
import sys
from typing import List

from src.extractor import ContentExtractor, ExtractionConfig
from src.validator import ContentValidator, ValidationConfig
from src.embedder import EmbeddingGenerator, EmbeddingConfig
from src.storage import VectorStorage, VectorStorageConfig
from src.pipeline import PipelineManager
from src.lib.config import config


def create_pipeline_components():
    """Create and configure all pipeline components."""
    # Create extractor
    extraction_config = ExtractionConfig(
        timeout=config.EXTRACTION_TIMEOUT,
        max_retries=config.MAX_RETRIES
    )
    extractor = ContentExtractor(extraction_config)

    # Create validator
    validation_config = ValidationConfig(
        min_content_length=50,
        max_content_length=100000,
        min_quality_score=0.5,
        min_word_count=10
    )
    validator = ContentValidator(validation_config)

    # Create embedder
    embedding_config = EmbeddingConfig(
        api_key=config.COHERE_API_KEY,
        model="embed-english-v3.0",
        batch_size=96,
        max_retries=config.MAX_RETRIES,
        timeout=config.TIMEOUT
    )
    embedder = EmbeddingGenerator(embedding_config)

    # Create storage
    vector_config = VectorStorageConfig(
        host=config.QDRANT_HOST,
        port=config.QDRANT_PORT,
        api_key=config.QDRANT_API_KEY,
        url=config.QDRANT_URL,
        collection_name=config.COLLECTION_NAME,
        timeout=config.TIMEOUT,
        max_retries=config.MAX_RETRIES
    )
    storage = VectorStorage(vector_config)

    # Create pipeline manager
    pipeline_manager = PipelineManager(config.get_pipeline_config())

    # Set components
    pipeline_manager.set_components(extractor, validator, embedder, storage)

    return pipeline_manager


def run_pipeline(urls: List[str]):
    """Run the embedding pipeline on the specified URLs."""
    try:
        # Validate configuration
        config.validate()

        # Create pipeline components
        pipeline_manager = create_pipeline_components()

        # Run the pipeline
        results = pipeline_manager.run_pipeline(urls)

        # Print results
        successful = sum(1 for r in results if r.status == "success")
        failed = len(results) - successful

        print(f"Pipeline completed: {successful} successful, {failed} failed")

        for result in results:
            status = "✓" if result.status == "success" else "✗"
            print(f"{status} {result.url}: {result.status}")

        return results

    except Exception as e:
        print(f"Error running pipeline: {str(e)}", file=sys.stderr)
        return []


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Embedding Pipeline CLI")
    parser.add_argument("urls", nargs="+", help="URLs to process")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

    results = run_pipeline(args.urls)

    # Exit with error code if any URLs failed
    if results and any(r.status == "failed" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()