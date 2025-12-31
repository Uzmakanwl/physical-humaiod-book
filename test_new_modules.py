"""
Test script to verify that new modules can be imported and used correctly.
"""
def test_new_modules():
    """Test that new modules can be imported and used without errors."""
    print("Testing new module imports and functionality...")

    try:
        from src.lib.validators import is_valid_url, sanitize_url, is_safe_url
        print("[OK] Validators module imported successfully")

        # Test basic functionality
        test_url = "https://example.com"
        assert is_valid_url(test_url) == True
        assert sanitize_url(test_url) == test_url
        assert is_safe_url(test_url) == True
        print("[OK] Basic validator functions work correctly")
    except ImportError as e:
        print(f"[ERROR] Failed to import Validators: {e}")
    except AssertionError as e:
        print(f"[ERROR] Validator functions failed basic test: {e}")
    except Exception as e:
        print(f"[ERROR] Error testing validator functions: {e}")

    try:
        from src.lib.structure import preserve_document_hierarchy, create_document_outline
        print("[OK] Structure module imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import Structure: {e}")

    try:
        from src.lib.utils import retry_on_failure, time_it, chunk_list
        print("[OK] Utils module imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import Utils: {e}")

    try:
        # Test the main library import
        from src.lib import (
            is_valid_url, sanitize_url, is_safe_url,
            preserve_document_hierarchy, create_document_outline,
            retry_on_failure, time_it, chunk_list
        )
        print("[OK] Main library imports work correctly")
    except ImportError as e:
        print(f"[ERROR] Failed to import from main library: {e}")

    print("\nNew module testing completed!")


if __name__ == "__main__":
    test_new_modules()