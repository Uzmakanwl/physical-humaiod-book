"""
Test script to verify that all modules can be imported correctly.
"""
def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing module imports...")

    try:
        from src.extractor import ContentExtractor, ExtractionConfig
        print("[OK] ContentExtractor imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import ContentExtractor: {e}")

    try:
        from src.validator import ContentValidator, ValidationConfig
        print("[OK] ContentValidator imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import ContentValidator: {e}")

    try:
        from src.embedder import EmbeddingGenerator, EmbeddingConfig
        print("[OK] EmbeddingGenerator imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import EmbeddingGenerator: {e}")

    try:
        from src.storage import VectorStorage, VectorStorageConfig
        print("[OK] VectorStorage imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import VectorStorage: {e}")

    try:
        from src.pipeline import PipelineManager, PipelineConfig
        print("[OK] PipelineManager imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import PipelineManager: {e}")

    try:
        from src.lib.config import Config, config
        print("[OK] Config imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import Config: {e}")

    try:
        from src.lib.utils import retry_on_failure, time_it, chunk_list
        print("[OK] Utils imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import Utils: {e}")

    try:
        from src.models.models import ContentExtractionResult, EmbeddingResult
        print("[OK] Models imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import Models: {e}")

    try:
        from src import ContentExtractor, ContentValidator, EmbeddingGenerator, VectorStorage, PipelineManager
        print("[OK] Main package imports work")
    except ImportError as e:
        print(f"[ERROR] Failed to import from main package: {e}")

    print("\nImport testing completed!")


if __name__ == "__main__":
    test_imports()