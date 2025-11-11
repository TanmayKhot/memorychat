#!/usr/bin/env python3
"""
Test script for Step 5.4: Error Handling and Validation
Tests error handlers and validation middleware.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory
os.chdir(backend_dir)

from unittest.mock import Mock, MagicMock, patch
from fastapi import Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DatabaseError
from pydantic import ValidationError
from openai import APIError, RateLimitError, APIConnectionError

try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = None

from services.error_handler import (
    ProfileNotFoundException,
    SessionNotFoundException,
    InvalidPrivacyModeException,
    MemoryLimitExceededException,
    TokenLimitExceededException,
    LLMException,
    DatabaseException,
    UserNotFoundException,
    ValidationException,
)
from api.middleware.error_handler import (
    create_error_response,
    sanitize_error_message,
    generate_request_id,
    http_exception_handler,
    validation_error_handler,
    database_error_handler,
    llm_error_handler,
    memorychat_exception_handler,
    general_exception_handler,
)
from api.middleware.validation import (
    validate_session_belongs_to_user,
    validate_profile_belongs_to_user,
    validate_privacy_mode_transition,
    check_memory_limit,
    check_session_limit,
    check_message_limit,
)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_check(description: str, passed: bool, details: str = ""):
    """Print a check result."""
    status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    print(f"  {status} {description}")
    if details and passed:
        print(f"    {Colors.BLUE}→{Colors.RESET} {details}")


def test_custom_exceptions():
    """Test custom exception classes."""
    print_header("TESTING CUSTOM EXCEPTIONS")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Test ProfileNotFoundException
        checks_total += 1
        exc = ProfileNotFoundException(123)
        if exc.error_code == "PROFILE_NOT_FOUND" and exc.details["profile_id"] == 123:
            checks_passed += 1
            print_check("ProfileNotFoundException works correctly", True)
        else:
            print_check("ProfileNotFoundException works correctly", False)
        
        # Test SessionNotFoundException
        checks_total += 1
        exc = SessionNotFoundException(456)
        if exc.error_code == "SESSION_NOT_FOUND" and exc.details["session_id"] == 456:
            checks_passed += 1
            print_check("SessionNotFoundException works correctly", True)
        else:
            print_check("SessionNotFoundException works correctly", False)
        
        # Test InvalidPrivacyModeException
        checks_total += 1
        exc = InvalidPrivacyModeException("invalid", ["normal", "incognito"])
        if exc.error_code == "INVALID_PRIVACY_MODE":
            checks_passed += 1
            print_check("InvalidPrivacyModeException works correctly", True)
        else:
            print_check("InvalidPrivacyModeException works correctly", False)
        
        # Test MemoryLimitExceededException
        checks_total += 1
        exc = MemoryLimitExceededException(100, 150)
        if exc.error_code == "MEMORY_LIMIT_EXCEEDED" and exc.details["limit"] == 100:
            checks_passed += 1
            print_check("MemoryLimitExceededException works correctly", True)
        else:
            print_check("MemoryLimitExceededException works correctly", False)
        
        # Test TokenLimitExceededException
        checks_total += 1
        exc = TokenLimitExceededException(1000, 1500, "TestAgent")
        if exc.error_code == "TOKEN_LIMIT_EXCEEDED" and exc.details["agent"] == "TestAgent":
            checks_passed += 1
            print_check("TokenLimitExceededException works correctly", True)
        else:
            print_check("TokenLimitExceededException works correctly", False)
        
        # Test to_dict method
        checks_total += 1
        exc = ProfileNotFoundException(123)
        exc_dict = exc.to_dict()
        if "error" in exc_dict and "error_code" in exc_dict and "details" in exc_dict:
            checks_passed += 1
            print_check("Exception.to_dict() works correctly", True)
        else:
            print_check("Exception.to_dict() works correctly", False)
        
    except Exception as e:
        print_check("Custom exceptions", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_error_response_creation():
    """Test error response creation."""
    print_header("TESTING ERROR RESPONSE CREATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Test create_error_response
        checks_total += 1
        response = create_error_response(
            error="TestError",
            detail="Test detail",
            error_code="TEST_ERROR",
            status_code=400
        )
        
        if response.status_code == 400:
            checks_passed += 1
            print_check("create_error_response creates correct status code", True)
        else:
            print_check("create_error_response creates correct status code", False)
        
        # Test response content
        checks_total += 1
        content = response.body.decode()
        if "TestError" in content and "TEST_ERROR" in content:
            checks_passed += 1
            print_check("create_error_response includes error information", True)
        else:
            print_check("create_error_response includes error information", False)
        
        # Test request ID
        checks_total += 1
        request_id = generate_request_id()
        response = create_error_response(
            error="TestError",
            detail="Test detail",
            request_id=request_id
        )
        content = response.body.decode()
        if request_id in content:
            checks_passed += 1
            print_check("create_error_response includes request ID", True)
        else:
            print_check("create_error_response includes request ID", False)
        
        # Test timestamp
        checks_total += 1
        content = response.body.decode()
        if "timestamp" in content:
            checks_passed += 1
            print_check("create_error_response includes timestamp", True)
        else:
            print_check("create_error_response includes timestamp", False)
        
    except Exception as e:
        print_check("Error response creation", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_sanitize_error_message():
    """Test error message sanitization."""
    print_header("TESTING ERROR MESSAGE SANITIZATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Test API key hiding
        checks_total += 1
        message = "API key: sk-1234567890abcdefghijklmnopqrstuvwxyz"
        sanitized = sanitize_error_message(message)
        if "sk-***" in sanitized:
            checks_passed += 1
            print_check("Sanitization hides API keys", True)
        else:
            print_check("Sanitization hides API keys", False, f"Got: {sanitized}")
        
        # Test email hiding
        checks_total += 1
        message = "User email: test@example.com"
        sanitized = sanitize_error_message(message)
        if "***@example.com" in sanitized:
            checks_passed += 1
            print_check("Sanitization hides email addresses", True)
        else:
            print_check("Sanitization hides email addresses", False)
        
    except Exception as e:
        print_check("Error message sanitization", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


async def test_exception_handlers():
    """Test exception handlers."""
    print_header("TESTING EXCEPTION HANDLERS")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        
        # Test HTTPException handler
        checks_total += 1
        exc = HTTPException(status_code=404, detail="Not found")
        response = await http_exception_handler(mock_request, exc)
        if response.status_code == 404:
            checks_passed += 1
            print_check("HTTPException handler works", True)
        else:
            print_check("HTTPException handler works", False)
        
        # Test MemoryChatException handler
        checks_total += 1
        exc = ProfileNotFoundException(123)
        response = await memorychat_exception_handler(mock_request, exc)
        if response.status_code == 404:
            checks_passed += 1
            print_check("MemoryChatException handler works", True)
        else:
            print_check("MemoryChatException handler works", False)
        
        # Test general exception handler
        checks_total += 1
        exc = ValueError("Test error")
        response = await general_exception_handler(mock_request, exc)
        if response.status_code == 500:
            checks_passed += 1
            print_check("General exception handler works", True)
        else:
            print_check("General exception handler works", False)
        
    except Exception as e:
        print_check("Exception handlers", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_validation_functions():
    """Test validation functions."""
    print_header("TESTING VALIDATION FUNCTIONS")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Test privacy mode validation
        checks_total += 1
        try:
            validate_privacy_mode_transition("normal", "incognito")
            checks_passed += 1
            print_check("Privacy mode transition validation works", True)
        except Exception:
            print_check("Privacy mode transition validation works", False)
        
        # Test invalid privacy mode
        checks_total += 1
        try:
            validate_privacy_mode_transition("normal", "invalid")
            print_check("Invalid privacy mode raises exception", False)
        except InvalidPrivacyModeException:
            checks_passed += 1
            print_check("Invalid privacy mode raises exception", True)
        except Exception:
            print_check("Invalid privacy mode raises exception", False)
        
    except Exception as e:
        print_check("Validation functions", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


async def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'ERROR HANDLING AND VALIDATION TEST - STEP 5.4'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Run all tests
    passed, checks = test_custom_exceptions()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_error_response_creation()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_sanitize_error_message()
    total_passed += passed
    total_checks += checks
    
    passed, checks = await test_exception_handlers()
    total_passed += passed
    total_checks += checks
    
    passed, checks = test_validation_functions()
    total_passed += passed
    total_checks += checks
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"  Total Checks: {total_checks}")
    print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {total_checks - total_passed}{Colors.RESET}")
    
    if total_passed == total_checks:
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}✗ SOME TESTS FAILED{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

