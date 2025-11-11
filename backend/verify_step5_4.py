#!/usr/bin/env python3
"""
Verification script for Step 5.4: Error Handling and Validation
Verifies structure and implementation.
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


def verify_error_handler_structure():
    """Verify error handler middleware structure."""
    print_header("VERIFYING ERROR HANDLER STRUCTURE")
    
    error_handler_file = backend_dir / "api" / "middleware" / "error_handler.py"
    if not error_handler_file.exists():
        print_check("error_handler.py exists", False)
        return False
    
    print_check("error_handler.py exists", True)
    
    with open(error_handler_file, 'r') as f:
        content = f.read()
    
    # Check for required functions
    required_functions = [
        "generate_request_id",
        "sanitize_error_message",
        "create_error_response",
        "http_exception_handler",
        "validation_error_handler",
        "database_error_handler",
        "llm_error_handler",
        "memorychat_exception_handler",
        "general_exception_handler",
        "register_error_handlers",
    ]
    
    for func in required_functions:
        has_func = f"def {func}" in content or f"async def {func}" in content
        print_check(f"Function {func} defined", has_func)
    
    return True


def verify_validation_structure():
    """Verify validation middleware structure."""
    print_header("VERIFYING VALIDATION MIDDLEWARE STRUCTURE")
    
    validation_file = backend_dir / "api" / "middleware" / "validation.py"
    if not validation_file.exists():
        print_check("validation.py exists", False)
        return False
    
    print_check("validation.py exists", True)
    
    with open(validation_file, 'r') as f:
        content = f.read()
    
    # Check for required functions
    required_functions = [
        "validate_session_belongs_to_user",
        "validate_profile_belongs_to_user",
        "validate_privacy_mode_transition",
        "check_memory_limit",
        "check_session_limit",
        "check_message_limit",
        "get_validated_session",
        "get_validated_profile",
    ]
    
    for func in required_functions:
        has_func = f"def {func}" in content
        print_check(f"Function {func} defined", has_func)
    
    return True


def verify_custom_exceptions():
    """Verify custom exceptions are defined."""
    print_header("VERIFYING CUSTOM EXCEPTIONS")
    
    error_handler_service = backend_dir / "services" / "error_handler.py"
    if not error_handler_service.exists():
        print_check("services/error_handler.py exists", False)
        return False
    
    print_check("services/error_handler.py exists", True)
    
    with open(error_handler_service, 'r') as f:
        content = f.read()
    
    # Check for required exceptions
    required_exceptions = [
        "ProfileNotFoundException",
        "SessionNotFoundException",
        "InvalidPrivacyModeException",
        "MemoryLimitExceededException",
        "TokenLimitExceededException",
        "UserNotFoundException",
        "LLMException",
        "DatabaseException",
        "ValidationException",
    ]
    
    for exc in required_exceptions:
        has_exc = f"class {exc}" in content
        print_check(f"Exception {exc} defined", has_exc)
    
    return True


def verify_main_integration():
    """Verify main.py integrates error handlers."""
    print_header("VERIFYING MAIN.PY INTEGRATION")
    
    main_file = backend_dir / "main.py"
    if not main_file.exists():
        print_check("main.py exists", False)
        return False
    
    print_check("main.py exists", True)
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for error handler registration
    has_import = "from api.middleware.error_handler import register_error_handlers" in content
    print_check("Error handler imported", has_import)
    
    has_registration = "register_error_handlers" in content
    print_check("Error handlers registered", has_registration)
    
    return True


def verify_imports():
    """Verify imports work."""
    print_header("VERIFYING IMPORTS")
    
    # Try to activate virtual environment if it exists
    venv_path = backend_dir / ".venv"
    if venv_path.exists():
        import sys
        venv_site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
            sys.path.insert(0, str(venv_site_packages))
    
    try:
        from api.middleware.error_handler import register_error_handlers
        print_check("Error handler imports successfully", True)
    except ImportError as e:
        if "fastapi" in str(e).lower() or "sqlalchemy" in str(e).lower():
            print_check("Error handler imports successfully", False,
                       f"Dependencies not installed. Run: pip install -r requirements.txt")
        else:
            print_check("Error handler imports successfully", False, str(e))
    except Exception as e:
        print_check("Error handler imports successfully", False, str(e))
    
    try:
        from api.middleware.validation import validate_session_belongs_to_user
        print_check("Validation middleware imports successfully", True)
    except ImportError as e:
        if "fastapi" in str(e).lower() or "sqlalchemy" in str(e).lower():
            print_check("Validation middleware imports successfully", False,
                       f"Dependencies not installed. Run: pip install -r requirements.txt")
        else:
            print_check("Validation middleware imports successfully", False, str(e))
    except Exception as e:
        print_check("Validation middleware imports successfully", False, str(e))


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  STEP 5.4 VERIFICATION: ERROR HANDLING AND VALIDATION")
    print("=" * 70)
    
    verify_file_exists(backend_dir / "api" / "middleware" / "error_handler.py", "Error handler file")
    verify_file_exists(backend_dir / "api" / "middleware" / "validation.py", "Validation middleware file")
    verify_file_exists(backend_dir / "api" / "middleware" / "__init__.py", "Middleware __init__.py")
    
    verify_error_handler_structure()
    verify_validation_structure()
    verify_custom_exceptions()
    verify_main_integration()
    
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

