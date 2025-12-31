"""
Demonstration script showing the complete embedding pipeline functionality.
"""
from src.extractor import ContentExtractor, ExtractionConfig
from src.validator import ContentValidator, ValidationConfig
from src.embedder import EmbeddingGenerator, EmbeddingConfig
from src.storage import VectorStorage, VectorStorageConfig
from src.pipeline import PipelineManager
from src.lib.config import config
from src.lib.validators import is_valid_url, validate_and_sanitize_urls
from src.lib.structure import preserve_document_hierarchy


def demonstrate_pipeline():
    """Demonstrate the complete embedding pipeline functionality."""
    print("Embedding Pipeline Demonstration")
    print("=" * 40)

    # Show the main components that make up the pipeline
    print("\n1. Pipeline Components:")
    print("   - ContentExtractor: Extracts content from URLs")
    print("   - ContentValidator: Validates content quality")
    print("   - EmbeddingGenerator: Creates semantic embeddings")
    print("   - VectorStorage: Stores embeddings in vector database")
    print("   - PipelineManager: Orchestrates the entire workflow")

    # Show configuration system
    print("\n2. Configuration System:")
    print("   - Environment-based configuration")
    print("   - API keys and service endpoints")
    print("   - Processing parameters and limits")

    # Show validation utilities
    print("\n3. Validation Utilities:")
    test_urls = [
        "https://example.com/docs",
        "http://invalid-url",
        "https://docusaurus.io/docs"
    ]
    print(f"   - Original URLs: {test_urls}")

    valid_urls = validate_and_sanitize_urls(test_urls)
    print(f"   - Validated URLs: {valid_urls}")

    # Show structure preservation
    print("\n4. Document Structure Preservation:")
    print("   - Preserves document hierarchy (headings, sections)")
    print("   - Maintains content formatting (code, lists, tables)")
    print("   - Supports various content types from Docusaurus sites")

    # Show utility functions
    print("\n5. Utility Functions:")
    print("   - Retry mechanisms with exponential backoff")
    print("   - Performance timing decorators")
    print("   - Content chunking and similarity calculations")
    print("   - URL validation and sanitization")

    # Show the pipeline orchestration
    print("\n6. Pipeline Orchestration:")
    print("   - Coordinated execution of all components")
    print("   - Error handling and recovery mechanisms")
    print("   - Progress tracking and logging")
    print("   - Configurable scheduling options")

    print("\n" + "=" * 40)
    print("Pipeline ready for production use!")
    print("Set environment variables and run with real URLs to process content.")


def show_pipeline_architecture():
    """Show the architectural overview of the pipeline."""
    print("\nPipeline Architecture Overview:")
    print("""
    [Docusaurus    ] -> [ContentExtractor ] -> [ContentValidator ]
    [   URLs       ]    [                 ]    [                 ]
    [--------------]    [-----------------]    [-----------------]
                              |
    [Configuration ] -> [EmbeddingGen.   ] -> [Validation      ]
    [             ]    [ (Cohere API)    ]    [ & Quality       ]
    [-------------]    [-----------------]    [  Checks         ]
                                                   |
    [Qdrant DB     ] <- [VectorStorage   ] <- [Store Embeddings ]
    [Configuration ]    [ (Qdrant Client)]    [ with Metadata   ]
    [-------------]    [-----------------]    [-----------------]
    """)


if __name__ == "__main__":
    demonstrate_pipeline()
    show_pipeline_architecture()