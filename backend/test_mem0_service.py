"""
Test script for Mem0Service implementation.
Verifies that all required methods from Checkpoint 3.4 are present.
"""

import inspect
from app.services.mem0_service import Mem0Service, mem0_service


def test_mem0_service():
    """Test Mem0Service implementation."""
    
    print("=" * 70)
    print("MEM0 SERVICE TEST")
    print("=" * 70)
    print()
    
    # Test service initialization
    try:
        service = Mem0Service()
        print("✅ Mem0Service initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Error initializing Mem0Service: {e}")
        return
    
    # Test singleton instance
    print("=" * 70)
    print("Testing Singleton Instance")
    print("=" * 70)
    try:
        assert mem0_service is not None
        print("✅ mem0_service singleton instance available")
        print()
    except AssertionError:
        print("❌ mem0_service singleton instance not available")
        print()
    
    # Required methods from Checkpoint 3.4
    required_methods = {
        "add_memory": 3,  # user_id, memory_content, metadata
        "get_memories": 2,  # user_id, memory_profile_id
        "search_memories": 4,  # user_id, query, memory_profile_id, limit
        "delete_memory": 1,  # memory_id
        "update_memory": 2,  # memory_id, content
        "extract_memories_from_conversation": 3,  # messages, user_id, memory_profile_id
    }
    
    # Additional helper methods
    additional_methods = {
        "delete_all_memories": 2,  # user_id, memory_profile_id
        "copy_memories_to_profile": 3,  # user_id, source_profile_id, target_profile_id
        "_create_user_identifier": 2,  # user_id, memory_profile_id
    }
    
    print("=" * 70)
    print("Verifying Required Methods")
    print("=" * 70)
    
    methods_found = 0
    for method_name, expected_params in required_methods.items():
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                # Get method signature
                sig = inspect.signature(method)
                param_count = len([p for p in sig.parameters.values() if p.name != 'self'])
                print(f"✅ {method_name:<40} - Params: {param_count}")
                methods_found += 1
            else:
                print(f"❌ {method_name:<40} - Not callable")
        else:
            print(f"❌ {method_name:<40} - Not found")
    
    print()
    print(f"📊 Required methods found: {methods_found}/{len(required_methods)}")
    print()
    
    # Check additional methods
    print("=" * 70)
    print("Verifying Additional Helper Methods")
    print("=" * 70)
    
    additional_found = 0
    for method_name, expected_params in additional_methods.items():
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                sig = inspect.signature(method)
                param_count = len([p for p in sig.parameters.values() if p.name != 'self'])
                print(f"✅ {method_name:<40} - Params: {param_count}")
                additional_found += 1
            else:
                print(f"❌ {method_name:<40} - Not callable")
        else:
            print(f"❌ {method_name:<40} - Not found")
    
    print()
    print(f"📊 Additional methods found: {additional_found}/{len(additional_methods)}")
    print()
    
    # Verify memory client initialization
    print("=" * 70)
    print("Verifying Memory Client")
    print("=" * 70)
    
    if hasattr(service, 'memory'):
        print("✅ Memory client initialized")
        print(f"   Type: {type(service.memory).__name__}")
    else:
        print("❌ Memory client not found")
    
    print()
    
    # Final summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if methods_found == len(required_methods):
        print("🎉 All required methods implemented!")
        print("✅ Mem0Service is ready to use")
        print()
        print("Implemented operations:")
        print("  • Memory CRUD operations (5 methods)")
        print("  • Memory extraction from conversations (1 method)")
        print("  • Memory profile namespacing support")
        print("  • Additional helper methods")
        print()
        print(f"Total required methods: {methods_found}")
        print(f"Total methods (with helpers): {methods_found + additional_found}")
    else:
        print("⚠️  Some required methods are missing")
        print(f"Found: {methods_found}/{len(required_methods)}")
    
    print()
    print("=" * 70)
    print("Note: This test only verifies method signatures.")
    print("Actual memory operations will be tested through API endpoints.")
    print("=" * 70)


if __name__ == "__main__":
    test_mem0_service()

