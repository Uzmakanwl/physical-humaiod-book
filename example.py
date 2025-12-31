"""
Example script to demonstrate the embedding pipeline functionality.
"""
from src.extractor import ContentExtractor, ExtractionConfig
from src.validator import ContentValidator, ValidationConfig
from src.embedder import EmbeddingGenerator, EmbeddingConfig
from src.storage import VectorStorage, VectorStorageConfig
from src.pipeline import PipelineManager
from src.lib.config import config


def main():
    """Run a simple example of the embedding pipeline."""
    print("Embedding Pipeline Example")
    print("=" * 30)

    # Validate configuration
    try:
        config.validate()
        print("[OK] Configuration validated")
    except ValueError as e:
        print(f"X Configuration error: {e}")
        print("Please set the required environment variables:")
        print("- COHERE_API_KEY")
        print("- QDRANT_HOST (optional, defaults to localhost)")
        print("- QDRANT_PORT (optional, defaults to 6333)")
        print("- QDRANT_API_KEY (optional)")
        return

    # Create extractor
    extraction_config = ExtractionConfig(timeout=30, max_retries=3)
    extractor = ContentExtractor(extraction_config)
    print("[OK] Content extractor created")

    # Create validator
    validation_config = ValidationConfig(min_content_length=50, min_quality_score=0.3)
    validator = ContentValidator(validation_config)
    print("[OK] Content validator created")

    # Create embedder
    embedding_config = EmbeddingConfig(
        api_key=config.COHERE_API_KEY,
        model="embed-english-v3.0",
        batch_size=10
    )
    embedder = EmbeddingGenerator(embedding_config)
    print("[OK] Embedding generator created")

    # Create storage
    vector_config = VectorStorageConfig(
        host=config.QDRANT_HOST,
        port=config.QDRANT_PORT,
        api_key=config.QDRANT_API_KEY,
        collection_name=config.COLLECTION_NAME
    )
    storage = VectorStorage(vector_config)
    print("[OK] Vector storage created")

    # Create pipeline manager
    pipeline_manager = PipelineManager(config.get_pipeline_config())
    pipeline_manager.set_components(extractor, validator, embedder, storage)
    print("[OK] Pipeline manager created")

    # Example URL to process (you can change this to any Docusaurus documentation URL)
    example_urls = [
        "https://docusaurus.io/docs",
        "https://docusaurus.io/docs/getting-started"
    ]

    print(f"\nProcessing example URLs: {example_urls}")

    # Process the URLs
    results = pipeline_manager.run_pipeline(example_urls)

    print(f"\nProcessing completed:")
    for result in results:
        status_icon = "[OK]" if result.status == "success" else "[ERROR]"
        print(f"{status_icon} {result.url} - {result.status}")
        if result.errors:
            print(f"  Errors: {result.errors}")

    print(f"\nPipeline execution completed!")


if __name__ == "__main__":
    main()