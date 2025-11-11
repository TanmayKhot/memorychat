#!/usr/bin/env python3
"""
Verification script for Step 5.3: ChatService Integration
Verifies structure and implementation without requiring server to be running.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

checks_passed = 0
checks_total = 0


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(name: str, passed: bool, details: str = ""):
    """Print check result."""
    global checks_passed, checks_total
    checks_total += 1
    status = "✓" if passed else "✗"
    print(f"  {status} {name}")
    if details:
        print(f"    {details}")
    if passed:
        checks_passed += 1


def verify_file_exists(filepath: Path, description: str):
    """Verify file exists."""
    exists = filepath.exists()
    print_check(f"{description} exists", exists, str(filepath))
    return exists


def verify_chat_service_structure():
    """Verify ChatService class structure."""
    print_header("VERIFYING CHATSERVICE STRUCTURE")
    
    chat_service_file = backend_dir / "services" / "chat_service.py"
    if not chat_service_file.exists():
        print_check("chat_service.py file exists", False)
        return False
    
    print_check("chat_service.py file exists", True)
    
    # Read file content
    with open(chat_service_file, 'r') as f:
        content = f.read()
    
    # Check for ChatService class
    has_class = "class ChatService" in content
    print_check("ChatService class defined", has_class)
    
    # Check for required methods
    required_methods = [
        "__init__",
        "process_message",
        "_prepare_agent_input",
        "_save_conversation",
        "_save_memories",
        "_handle_privacy_mode"
    ]
    
    for method in required_methods:
        has_method = f"def {method}" in content
        print_check(f"Method {method} defined", has_method)
    
    # Check for imports
    has_imports = (
        "from agents.context_coordinator_agent import ContextCoordinatorAgent" in content and
        "from services.database_service import DatabaseService" in content and
        "from services.vector_service import VectorService" in content
    )
    print_check("Required imports present", has_imports)
    
    return True


def verify_chat_endpoint_uses_service():
    """Verify chat endpoint uses ChatService."""
    print_header("VERIFYING CHAT ENDPOINT INTEGRATION")
    
    chat_endpoint_file = backend_dir / "api" / "endpoints" / "chat.py"
    if not chat_endpoint_file.exists():
        print_check("chat.py endpoint file exists", False)
        return False
    
    print_check("chat.py endpoint file exists", True)
    
    # Read file content
    with open(chat_endpoint_file, 'r') as f:
        content = f.read()
    
    # Check for ChatService import
    has_import = "from services.chat_service import ChatService" in content
    print_check("ChatService imported in chat endpoint", has_import)
    
    # Check for ChatService usage
    has_usage = "ChatService(" in content
    print_check("ChatService instantiated in endpoint", has_usage)
    
    # Check for process_message call
    has_call = "process_message" in content
    print_check("process_message method called", has_call)
    
    return True


def verify_coordinator_includes_memories():
    """Verify coordinator includes memories in response."""
    print_header("VERIFYING COORDINATOR MEMORY INTEGRATION")
    
    coordinator_file = backend_dir / "agents" / "context_coordinator_agent.py"
    if not coordinator_file.exists():
        print_check("context_coordinator_agent.py exists", False)
        return False
    
    print_check("context_coordinator_agent.py exists", True)
    
    # Read file content
    with open(coordinator_file, 'r') as f:
        content = f.read()
    
    # Check for extracted_memories in aggregate_results
    has_memories = "extracted_memories" in content
    print_check("extracted_memories included in response", has_memories)
    
    return True


def verify_imports():
    """Verify all imports work."""
    print_header("VERIFYING IMPORTS")
    
    # Try to activate virtual environment if it exists
    venv_path = backend_dir / ".venv"
    if venv_path.exists():
        import sys
        venv_site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
            sys.path.insert(0, str(venv_site_packages))
    
    try:
        from services.chat_service import ChatService
        print_check("ChatService imports successfully", True)
    except ImportError as e:
        # Check if it's a dependency issue
        if "sqlalchemy" in str(e).lower() or "fastapi" in str(e).lower():
            print_check("ChatService imports successfully", False, 
                       f"Dependencies not installed. Run: pip install -r requirements.txt")
        else:
            print_check("ChatService imports successfully", False, str(e))
    except Exception as e:
        print_check("ChatService imports successfully", False, str(e))
    
    try:
        from api.endpoints.chat import router
        print_check("Chat endpoint imports successfully", True)
    except ImportError as e:
        # Check if it's a dependency issue
        if "fastapi" in str(e).lower() or "sqlalchemy" in str(e).lower():
            print_check("Chat endpoint imports successfully", False,
                       f"Dependencies not installed. Run: pip install -r requirements.txt")
        else:
            print_check("Chat endpoint imports successfully", False, str(e))
    except Exception as e:
        print_check("Chat endpoint imports successfully", False, str(e))


def verify_method_signatures():
    """Verify method signatures are correct."""
    print_header("VERIFYING METHOD SIGNATURES")
    
    chat_service_file = backend_dir / "services" / "chat_service.py"
    if not chat_service_file.exists():
        return False
    
    with open(chat_service_file, 'r') as f:
        content = f.read()
    
    # Check process_message signature
    has_process = "def process_message(" in content and "session_id: int" in content and "user_message: str" in content
    print_check("process_message has correct signature", has_process)
    
    # Check _prepare_agent_input signature
    has_prepare = "def _prepare_agent_input(" in content
    print_check("_prepare_agent_input defined", has_prepare)
    
    # Check _save_conversation signature
    has_save_conv = "def _save_conversation(" in content
    print_check("_save_conversation defined", has_save_conv)
    
    # Check _save_memories signature
    has_save_mem = "def _save_memories(" in content
    print_check("_save_memories defined", has_save_mem)
    
    # Check _handle_privacy_mode signature
    has_handle = "def _handle_privacy_mode(" in content
    print_check("_handle_privacy_mode defined", has_handle)
    
    return True


def verify_error_handling():
    """Verify error handling is in place."""
    print_header("VERIFYING ERROR HANDLING")
    
    chat_service_file = backend_dir / "services" / "chat_service.py"
    if not chat_service_file.exists():
        return False
    
    with open(chat_service_file, 'r') as f:
        content = f.read()
    
    # Check for error handling
    has_try_except = "try:" in content and "except" in content
    print_check("Error handling present", has_try_except)
    
    # Check for ValueError handling
    has_value_error = "ValueError" in content
    print_check("ValueError handling", has_value_error)
    
    # Check for RuntimeError handling
    has_runtime_error = "RuntimeError" in content
    print_check("RuntimeError handling", has_runtime_error)
    
    return True


def verify_logging():
    """Verify logging is implemented."""
    print_header("VERIFYING LOGGING")
    
    chat_service_file = backend_dir / "services" / "chat_service.py"
    if not chat_service_file.exists():
        return False
    
    with open(chat_service_file, 'r') as f:
        content = f.read()
    
    # Check for logger
    has_logger = "self.logger" in content
    print_check("Logger used in ChatService", has_logger)
    
    # Check for log_agent_action
    has_log_action = "log_agent_action" in content
    print_check("Agent actions logged", has_log_action)
    
    return True


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  STEP 5.3 VERIFICATION: CHATSERVICE INTEGRATION")
    print("=" * 70)
    
    verify_file_exists(backend_dir / "services" / "chat_service.py", "ChatService file")
    verify_chat_service_structure()
    verify_chat_endpoint_uses_service()
    verify_coordinator_includes_memories()
    verify_method_signatures()
    verify_error_handling()
    verify_logging()
    
    # Try imports if possible
    try:
        verify_imports()
    except Exception as e:
        print(f"\n  Note: Import verification skipped (dependencies may not be installed)")
        print(f"    Error: {str(e)}")
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    print(f"  Total Checks: {checks_total}")
    print(f"  Passed: {checks_passed}")
    print(f"  Failed: {checks_total - checks_passed}")
    
    if checks_passed == checks_total:
        print("\n  ✓ ALL CHECKS PASSED!")
        return 0
    else:
        print("\n  ✗ SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

