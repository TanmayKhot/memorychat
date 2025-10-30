"""
Quick verification script for Checkpoints 3.11 and 3.12.
Verifies that all modules can be imported and are properly structured.

Run with: python verify_checkpoints.py
"""

import sys


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def check_imports():
    """Verify all modules can be imported."""
    print_section("CHECKING IMPORTS")
    
    imports_to_check = [
        ("app.api.v1.endpoints.sessions", "Sessions endpoint"),
        ("app.api.v1.endpoints.chat", "Chat endpoint"),
        ("app.services.chat_service", "Chat service"),
        ("app.services.supabase_service", "Supabase service"),
        ("app.services.mem0_service", "Mem0 service"),
        ("app.services.llm_service", "LLM service"),
        ("app.schemas.chat", "Chat schemas"),
        ("app.core.security", "Security module"),
    ]
    
    all_passed = True
    for module_name, description in imports_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {description}: {module_name}")
        except Exception as e:
            print(f"  ❌ {description}: {module_name}")
            print(f"     Error: {e}")
            all_passed = False
    
    return all_passed


def check_endpoints():
    """Verify endpoints are properly defined."""
    print_section("CHECKING ENDPOINTS")
    
    try:
        from app.api.v1.endpoints import sessions, chat
        
        # Check sessions endpoints
        sessions_endpoints = [
            ("get_sessions", "GET /sessions"),
            ("create_session", "POST /sessions"),
            ("get_session", "GET /sessions/{session_id}"),
            ("update_session", "PUT /sessions/{session_id}"),
            ("delete_session", "DELETE /sessions/{session_id}"),
            ("get_session_messages", "GET /sessions/{session_id}/messages"),
        ]
        
        print("\n  Sessions Endpoints:")
        all_present = True
        for func_name, endpoint in sessions_endpoints:
            if hasattr(sessions, func_name):
                print(f"    ✅ {endpoint}: {func_name}()")
            else:
                print(f"    ❌ {endpoint}: {func_name}() NOT FOUND")
                all_present = False
        
        # Check chat endpoints
        chat_endpoints = [
            ("send_message", "POST /chat/{session_id}"),
            ("stream_message", "POST /chat/{session_id}/stream"),
        ]
        
        print("\n  Chat Endpoints:")
        for func_name, endpoint in chat_endpoints:
            if hasattr(chat, func_name):
                print(f"    ✅ {endpoint}: {func_name}()")
            else:
                print(f"    ❌ {endpoint}: {func_name}() NOT FOUND")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"  ❌ Error checking endpoints: {e}")
        return False


def check_router_integration():
    """Verify routers are integrated into main API."""
    print_section("CHECKING ROUTER INTEGRATION")
    
    try:
        from app.api.v1 import api_router
        
        # Get all routes
        routes = []
        for route in api_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    routes.append(f"{method} {route.path}")
        
        expected_routes = [
            # Sessions
            "GET /sessions",
            "POST /sessions",
            "GET /sessions/{session_id}",
            "PUT /sessions/{session_id}",
            "DELETE /sessions/{session_id}",
            "GET /sessions/{session_id}/messages",
            # Chat
            "POST /chat/{session_id}",
            "POST /chat/{session_id}/stream",
        ]
        
        all_found = True
        for expected in expected_routes:
            found = any(expected in route for route in routes)
            if found:
                print(f"  ✅ {expected}")
            else:
                print(f"  ❌ {expected} NOT FOUND")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"  ❌ Error checking router integration: {e}")
        return False


def check_schemas():
    """Verify all required schemas are defined."""
    print_section("CHECKING SCHEMAS")
    
    try:
        from app.schemas import chat
        
        schemas_to_check = [
            "ChatSessionCreate",
            "ChatSessionUpdate",
            "ChatSessionResponse",
            "ChatMessageResponse",
            "ChatRequest",
            "ChatResponse",
            "ChatStreamChunk",
            "PrivacyMode",
        ]
        
        all_present = True
        for schema_name in schemas_to_check:
            if hasattr(chat, schema_name):
                print(f"  ✅ {schema_name}")
            else:
                print(f"  ❌ {schema_name} NOT FOUND")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"  ❌ Error checking schemas: {e}")
        return False


def check_services():
    """Verify services have required methods."""
    print_section("CHECKING SERVICES")
    
    try:
        from app.services.chat_service import chat_service
        
        required_methods = [
            "process_user_message",
            "stream_user_message",
            "create_new_session",
            "get_session_details",
        ]
        
        all_present = True
        print("\n  ChatService methods:")
        for method_name in required_methods:
            if hasattr(chat_service, method_name):
                print(f"    ✅ {method_name}()")
            else:
                print(f"    ❌ {method_name}() NOT FOUND")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"  ❌ Error checking services: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print(" CHECKPOINT 3.11 & 3.12 VERIFICATION")
    print("=" * 70)
    
    results = []
    
    # Run checks
    results.append(("Module Imports", check_imports()))
    results.append(("Endpoint Functions", check_endpoints()))
    results.append(("Router Integration", check_router_integration()))
    results.append(("Schema Definitions", check_schemas()))
    results.append(("Service Methods", check_services()))
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
    
    print(f"\n  Total Checks: {total}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All verification checks passed!")
        print("\nCheckpoints 3.11 and 3.12 are properly implemented.")
        print("\nNext steps:")
        print("  1. Ensure server is running: uvicorn main:app --reload")
        print("  2. Test endpoints manually or run automated tests")
        print("  3. Verify with Swagger UI: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n⚠️  {failed} verification check(s) failed.")
        print("Please review the errors above and fix any issues.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

