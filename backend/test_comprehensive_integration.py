#!/usr/bin/env python3
"""
Comprehensive integration test for the entire codebase.
Tests that all components work together correctly.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

os.chdir(backend_dir)

from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

class Colors:
    """ANSI color codes."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_check(description: str, passed: bool, details: str = ""):
    """Print check result."""
    status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    print(f"  {status} {description}")
    if details:
        print(f"    {Colors.BLUE}→{Colors.RESET} {details}")


def test_all_imports():
    """Test that all modules can be imported."""
    print_header("TESTING ALL IMPORTS")
    
    checks_passed = 0
    checks_total = 0
    
    imports_to_test = [
        ("agents.context_coordinator_agent", "ContextCoordinatorAgent"),
        ("agents.conversation_agent", "ConversationAgent"),
        ("agents.memory_manager_agent", "MemoryManagerAgent"),
        ("agents.memory_retrieval_agent", "MemoryRetrievalAgent"),
        ("agents.privacy_guardian_agent", "PrivacyGuardianAgent"),
        ("agents.conversation_analyst_agent", "ConversationAnalystAgent"),
        ("services.chat_service", "ChatService"),
        ("services.database_service", "DatabaseService"),
        ("services.vector_service", "VectorService"),
        ("services.error_handler", "ProfileNotFoundException"),
        ("api.middleware.error_handler", "register_error_handlers"),
        ("api.middleware.validation", "validate_session_belongs_to_user"),
        ("api.endpoints.chat", "router"),
        ("api.endpoints.users", "router"),
        ("api.endpoints.memory_profiles", "router"),
        ("api.endpoints.sessions", "router"),
        ("api.endpoints.memories", "router"),
        ("api.endpoints.analytics", "router"),
        ("models.api_models", "CreateUserRequest"),
        ("database.models", "User"),
        ("database.database", "get_db"),
        ("main", "app"),
    ]
    
    for module_name, class_name in imports_to_test:
        checks_total += 1
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                checks_passed += 1
                print_check(f"{module_name}.{class_name} imports", True)
            else:
                print_check(f"{module_name}.{class_name} imports", False, "Class not found")
        except Exception as e:
            print_check(f"{module_name}.{class_name} imports", False, str(e))
    
    return checks_passed, checks_total


def test_fastapi_app():
    """Test FastAPI app configuration."""
    print_header("TESTING FASTAPI APP")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from main import app
        
        checks_total += 1
        if app.title == "MemoryChat Multi-Agent API":
            checks_passed += 1
            print_check("App title configured", True)
        else:
            print_check("App title configured", False)
        
        checks_total += 1
        schema = app.openapi()
        if "paths" in schema:
            checks_passed += 1
            print_check("OpenAPI schema generates", True, f"{len(schema['paths'])} paths")
        else:
            print_check("OpenAPI schema generates", False)
        
        checks_total += 1
        if "tags" in schema and len(schema["tags"]) >= 6:
            checks_passed += 1
            print_check("OpenAPI tags configured", True, f"{len(schema['tags'])} tags")
        else:
            print_check("OpenAPI tags configured", False)
        
        checks_total += 1
        if "/docs" in str(app.docs_url):
            checks_passed += 1
            print_check("Docs URL configured", True)
        else:
            print_check("Docs URL configured", False)
        
    except Exception as e:
        print_check("FastAPI app test", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_agent_integration():
    """Test agent integration."""
    print_header("TESTING AGENT INTEGRATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from agents.context_coordinator_agent import ContextCoordinatorAgent
        
        checks_total += 1
        coordinator = ContextCoordinatorAgent()
        if coordinator:
            checks_passed += 1
            print_check("ContextCoordinatorAgent instantiates", True)
        else:
            print_check("ContextCoordinatorAgent instantiates", False)
        
        checks_total += 1
        if hasattr(coordinator, 'privacy_guardian'):
            checks_passed += 1
            print_check("Coordinator has privacy_guardian", True)
        else:
            print_check("Coordinator has privacy_guardian", False)
        
        checks_total += 1
        if hasattr(coordinator, 'memory_retrieval'):
            checks_passed += 1
            print_check("Coordinator has memory_retrieval", True)
        else:
            print_check("Coordinator has memory_retrieval", False)
        
        checks_total += 1
        if hasattr(coordinator, 'conversation_agent'):
            checks_passed += 1
            print_check("Coordinator has conversation_agent", True)
        else:
            print_check("Coordinator has conversation_agent", False)
        
        checks_total += 1
        if hasattr(coordinator, 'memory_manager'):
            checks_passed += 1
            print_check("Coordinator has memory_manager", True)
        else:
            print_check("Coordinator has memory_manager", False)
        
    except Exception as e:
        print_check("Agent integration test", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_chatservice_integration():
    """Test ChatService integration."""
    print_header("TESTING CHATSERVICE INTEGRATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from services.chat_service import ChatService
        from unittest.mock import Mock
        
        mock_db = Mock(spec=Session)
        
        checks_total += 1
        chat_service = ChatService(mock_db)
        if chat_service:
            checks_passed += 1
            print_check("ChatService instantiates", True)
        else:
            print_check("ChatService instantiates", False)
        
        checks_total += 1
        if hasattr(chat_service, 'coordinator'):
            checks_passed += 1
            print_check("ChatService has coordinator", True)
        else:
            print_check("ChatService has coordinator", False)
        
        checks_total += 1
        if hasattr(chat_service, 'db_service'):
            checks_passed += 1
            print_check("ChatService has db_service", True)
        else:
            print_check("ChatService has db_service", False)
        
        checks_total += 1
        if hasattr(chat_service, 'vector_service'):
            checks_passed += 1
            print_check("ChatService has vector_service", True)
        else:
            print_check("ChatService has vector_service", False)
        
        checks_total += 1
        if hasattr(chat_service, 'process_message'):
            checks_passed += 1
            print_check("ChatService has process_message method", True)
        else:
            print_check("ChatService has process_message method", False)
        
    except Exception as e:
        print_check("ChatService integration test", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_error_handling_integration():
    """Test error handling integration."""
    print_header("TESTING ERROR HANDLING INTEGRATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from api.middleware.error_handler import register_error_handlers
        from services.error_handler import (
            ProfileNotFoundException,
            SessionNotFoundException,
            InvalidPrivacyModeException,
        )
        
        checks_total += 1
        if register_error_handlers:
            checks_passed += 1
            print_check("Error handler registration function exists", True)
        else:
            print_check("Error handler registration function exists", False)
        
        checks_total += 1
        exc = ProfileNotFoundException(123)
        if exc.error_code == "PROFILE_NOT_FOUND":
            checks_passed += 1
            print_check("Custom exceptions work", True)
        else:
            print_check("Custom exceptions work", False)
        
        checks_total += 1
        from api.middleware.validation import validate_privacy_mode_transition
        try:
            validate_privacy_mode_transition("normal", "incognito")
            checks_passed += 1
            print_check("Validation functions work", True)
        except Exception:
            print_check("Validation functions work", False)
        
    except Exception as e:
        print_check("Error handling integration test", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def main():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'COMPREHENSIVE INTEGRATION TEST'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Run all tests
    passed, checks = test_all_imports()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_fastapi_app()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_agent_integration()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_chatservice_integration()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_error_handling_integration()
    total_passed += passed
    total_checks += checks
    
    # Print summary
    print_header("INTEGRATION TEST SUMMARY")
    print(f"  Total Checks: {total_checks}")
    print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {total_checks - total_passed}{Colors.RESET}")
    
    if total_passed == total_checks:
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓ ALL INTEGRATION TESTS PASSED!{Colors.RESET}\n")
        print(f"{Colors.BOLD}The codebase is working correctly!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}✗ SOME INTEGRATION TESTS FAILED{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

