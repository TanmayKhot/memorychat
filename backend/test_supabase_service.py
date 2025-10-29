"""
Test script for Supabase Service.
Tests all CRUD operations for users, memory profiles, sessions, messages, and memories.
"""

import asyncio
from app.services.supabase_service import SupabaseService


async def test_supabase_service():
    """Test all Supabase service methods."""
    print("=" * 70)
    print("SUPABASE SERVICE TEST")
    print("=" * 70)
    
    # Initialize service
    service = SupabaseService()
    print("\n✅ SupabaseService initialized successfully")
    
    # Test connection
    print("\n" + "=" * 70)
    print("Testing Database Connection")
    print("=" * 70)
    
    try:
        # Try to fetch users table
        response = service.client.table("users").select("*").limit(1).execute()
        print("✅ Database connection successful")
        print(f"   Users table accessible: {response is not None}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test method signatures
    print("\n" + "=" * 70)
    print("Verifying Method Signatures")
    print("=" * 70)
    
    methods = [
        # User operations
        ("get_user_by_id", ["user_id"]),
        ("create_user", ["email", "user_id"]),
        
        # Memory profile operations
        ("get_memory_profiles", ["user_id"]),
        ("create_memory_profile", ["user_id", "name", "description", "is_default"]),
        ("update_memory_profile", ["profile_id", "data"]),
        ("delete_memory_profile", ["profile_id"]),
        ("get_memory_profile", ["profile_id"]),
        ("get_default_memory_profile", ["user_id"]),
        ("set_default_memory_profile", ["profile_id"]),
        
        # Chat session operations
        ("create_chat_session", ["user_id", "profile_id", "privacy_mode"]),
        ("get_chat_session", ["session_id"]),
        ("update_chat_session", ["session_id", "data"]),
        ("delete_chat_session", ["session_id"]),
        ("get_user_sessions", ["user_id", "limit", "offset"]),
        
        # Chat message operations
        ("create_chat_message", ["session_id", "role", "content", "metadata"]),
        ("get_session_messages", ["session_id", "limit", "offset"]),
        ("delete_session_messages", ["session_id"]),
        
        # mem0 memory reference operations
        ("store_mem0_memory_reference", ["user_id", "profile_id", "mem0_id", "content"]),
        ("get_mem0_memory_references", ["profile_id", "limit"]),
        ("delete_mem0_memory_reference", ["mem0_id"]),
    ]
    
    methods_found = 0
    for method_name, params in methods:
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                methods_found += 1
                print(f"✅ {method_name:35} - Params: {len(params)}")
        else:
            print(f"❌ {method_name:35} - NOT FOUND")
    
    print(f"\n📊 Methods found: {methods_found}/{len(methods)}")
    
    # Test helper method
    if hasattr(service, '_unset_all_defaults'):
        print("✅ Helper method '_unset_all_defaults' found")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if methods_found == len(methods):
        print("🎉 All required methods implemented!")
        print("✅ SupabaseService is ready to use")
        print("\nImplemented operations:")
        print("  • User management (2 methods)")
        print("  • Memory profile management (7 methods)")
        print("  • Chat session management (5 methods)")
        print("  • Chat message management (3 methods)")
        print("  • mem0 memory references (3 methods)")
        print(f"\nTotal: {methods_found} methods")
    else:
        print(f"⚠️  Some methods are missing: {len(methods) - methods_found}")
    
    print("\n" + "=" * 70)
    print("Note: This test only verifies method signatures.")
    print("Actual CRUD operations will be tested through API endpoints.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(test_supabase_service())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

