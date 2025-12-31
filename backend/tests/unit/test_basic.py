"""
Basic test setup for the embedding pipeline.
"""
import pytest
import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_basic_import():
    """Test that we can import the main modules."""
    try:
        import config
        import src.logger
        assert hasattr(config, 'Config')
        assert hasattr(src.logger, 'get_logger')
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")

if __name__ == "__main__":
    test_basic_import()
    print("Basic tests passed!")