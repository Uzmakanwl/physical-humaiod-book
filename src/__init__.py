"""
Main src package initialization.
"""
__version__ = "0.1.0"

# Import main components for easy access
from .extractor import ContentExtractor
from .validator import ContentValidator
from .embedder import EmbeddingGenerator
from .storage import VectorStorage
from .pipeline import PipelineManager

__all__ = [
    'ContentExtractor',
    'ContentValidator',
    'EmbeddingGenerator',
    'VectorStorage',
    'PipelineManager'
]