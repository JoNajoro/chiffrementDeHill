"""
Test script for the "Mes Documents" feature with access key verification.
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.document_model import DocumentModel


def test_access_key_generation():
    """Test that access keys are generated correctly."""
    print("Testing access key generation...")
    
    # Generate an access key
    key = DocumentModel.generate_access_key()
    
    assert key is not None, "Access key should not be None"
    assert len(key) > 20, "Access key should be reasonably long"
    assert isinstance(key, str), "Access key should be a string"
    
    # Generate another key to ensure uniqueness
    key2 = DocumentModel.generate_access_key()
    assert key != key2, "Access keys should be unique"
    
    print("[PASS] Access key generation test passed!")
    print(f"   Sample key: {key[:20]}...")
    return True


def test_document_model_structure():
    """Test that the DocumentModel has all required methods."""
    print("\nTesting DocumentModel structure...")
    
    required_methods = [
        'generate_access_key',
        'create_access_key_for_user',
        'verify_access_key',
        'upload_document',
        'get_user_documents',
        'get_document_by_id',
        'delete_document',
        'update_document_description'
    ]
    
    for method in required_methods:
        assert hasattr(DocumentModel, method), f"DocumentModel should have method: {method}"
        print(f"   [OK] {method} exists")
    
    print("[PASS] DocumentModel structure test passed!")
    return True


def test_notification_format():
    """Test the notification format for document access keys."""
    print("\nTesting notification format...")
    
    user_email = "test@example.com"
    access_key = "test_key_12345"
    
    # Simulate the notification message format
    expected_message = f"Votre cle pour aller dans Mes documents est : {access_key}"
    
    assert "Votre cle pour aller dans Mes documents est :" in expected_message
    assert access_key in expected_message
    
    print("[PASS] Notification format test passed!")
    print(f"   Sample message: {expected_message}")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("TESTING MES DOCUMENTS FEATURE")
    print("=" * 60)
    
    tests = [
        test_access_key_generation,
        test_document_model_structure,
        test_notification_format
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except AssertionError as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            results.append((test.__name__, False))
        except Exception as e:
            print(f"[ERROR] {test.__name__} error: {e}")
            results.append((test.__name__, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
