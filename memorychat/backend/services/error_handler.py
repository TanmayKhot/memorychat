"""
Error handling utilities for MemoryChat application.
Provides custom exceptions and error recovery strategies.
"""
from typing import Optional, Dict, Any, Callable

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config.logging_config import error_logger, app_logger


# ============================================================================
# Custom Exception Classes
# ============================================================================

class MemoryChatException(Exception):
    """Base exception for all MemoryChat application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize custom exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class DatabaseException(MemoryChatException):
    """Exception for database-related errors."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None
    ):
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            details={"operation": operation, "table": table}
        )


class ProfileNotFoundException(MemoryChatException):
    """Exception when memory profile is not found."""
    
    def __init__(self, profile_id: int):
        super().__init__(
            f"Memory profile with ID {profile_id} not found",
            error_code="PROFILE_NOT_FOUND",
            details={"profile_id": profile_id}
        )


class SessionNotFoundException(MemoryChatException):
    """Exception when chat session is not found."""
    
    def __init__(self, session_id: int):
        super().__init__(
            f"Chat session with ID {session_id} not found",
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id}
        )


class UserNotFoundException(MemoryChatException):
    """Exception when user is not found."""
    
    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        if user_id:
            message = f"User with ID {user_id} not found"
            details = {"user_id": user_id}
        elif email:
            message = f"User with email {email} not found"
            details = {"email": email}
        else:
            message = "User not found"
            details = {}
        
        super().__init__(
            message,
            error_code="USER_NOT_FOUND",
            details=details
        )


class InvalidPrivacyModeException(MemoryChatException):
    """Exception for invalid privacy mode."""
    
    def __init__(self, mode: str, valid_modes: list):
        super().__init__(
            f"Invalid privacy mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
            error_code="INVALID_PRIVACY_MODE",
            details={"provided_mode": mode, "valid_modes": valid_modes}
        )


class MemoryLimitExceededException(MemoryChatException):
    """Exception when memory limit is exceeded."""
    
    def __init__(self, limit: int, current: int):
        super().__init__(
            f"Memory limit exceeded. Limit: {limit}, Current: {current}",
            error_code="MEMORY_LIMIT_EXCEEDED",
            details={"limit": limit, "current": current}
        )


class TokenLimitExceededException(MemoryChatException):
    """Exception when token limit is exceeded."""
    
    def __init__(self, limit: int, used: int, agent_name: Optional[str] = None):
        super().__init__(
            f"Token limit exceeded. Limit: {limit}, Used: {used}",
            error_code="TOKEN_LIMIT_EXCEEDED",
            details={"limit": limit, "used": used, "agent": agent_name}
        )


class LLMException(MemoryChatException):
    """Exception for LLM/API related errors."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        super().__init__(
            message,
            error_code="LLM_ERROR",
            details={"provider": provider, "status_code": status_code}
        )


class VectorDatabaseException(MemoryChatException):
    """Exception for vector database (ChromaDB) errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message,
            error_code="VECTOR_DB_ERROR",
            details={"operation": operation}
        )


class ValidationException(MemoryChatException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            details={"field": field}
        )


# ============================================================================
# Error Recovery Strategies
# ============================================================================

class ErrorRecoveryStrategy:
    """Base class for error recovery strategies."""
    
    @staticmethod
    def should_retry(exception: Exception, attempt: int, max_attempts: int = 3) -> bool:
        """
        Determine if operation should be retried.
        
        Args:
            exception: The exception that occurred
            attempt: Current attempt number (1-indexed)
            max_attempts: Maximum number of attempts
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= max_attempts:
            return False
        
        # Retry on transient errors
        retryable_errors = (
            LLMException,
            DatabaseException,
            VectorDatabaseException,
        )
        
        return isinstance(exception, retryable_errors)
    
    @staticmethod
    def get_fallback_response(exception: Exception) -> Dict[str, Any]:
        """
        Get fallback response when operation fails.
        
        Args:
            exception: The exception that occurred
            
        Returns:
            Dictionary with fallback response data
        """
        if isinstance(exception, ProfileNotFoundException):
            return {
                "success": False,
                "error": "Memory profile not found. Please select a valid profile.",
                "fallback": True,
            }
        
        if isinstance(exception, SessionNotFoundException):
            return {
                "success": False,
                "error": "Chat session not found. Please start a new session.",
                "fallback": True,
            }
        
        if isinstance(exception, LLMException):
            return {
                "success": False,
                "error": "Unable to generate response. Please try again.",
                "fallback": True,
            }
        
        if isinstance(exception, MemoryLimitExceededException):
            return {
                "success": False,
                "error": "Memory limit reached. Please delete some memories.",
                "fallback": True,
            }
        
        # Generic fallback
        return {
            "success": False,
            "error": "An error occurred. Please try again.",
            "fallback": True,
        }


# ============================================================================
# Global Exception Handler
# ============================================================================

def handle_exception(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    log_error: bool = True
) -> Dict[str, Any]:
    """
    Handle an exception and return user-friendly error response.
    
    Args:
        exception: The exception to handle
        context: Optional context information (e.g., agent_name, session_id)
        log_error: Whether to log the error (default: True)
        
    Returns:
        Dictionary with error information for API response
    """
    context = context or {}
    
    # Log the error
    if log_error:
        error_logger.error(
            f"Exception handled: {type(exception).__name__} - {str(exception)}",
            exc_info=True,
            extra=context
        )
    
    # Handle custom exceptions
    if isinstance(exception, MemoryChatException):
        error_response = exception.to_dict()
    else:
        # Handle generic exceptions
        error_response = {
            "error": str(exception),
            "error_code": "UNKNOWN_ERROR",
            "details": {
                "exception_type": type(exception).__name__,
                "context": context,
            },
        }
    
    # Add timestamp
    from datetime import datetime
    error_response["timestamp"] = datetime.now().isoformat()
    
    # Add request ID if available
    if "request_id" in context:
        error_response["request_id"] = context["request_id"]
    
    return error_response


def format_error_message(exception: Exception, user_friendly: bool = True) -> str:
    """
    Format exception message for display.
    
    Args:
        exception: The exception to format
        user_friendly: Whether to return user-friendly message (default: True)
        
    Returns:
        Formatted error message
    """
    if isinstance(exception, MemoryChatException):
        return exception.message
    
    if user_friendly:
        # Return generic user-friendly message
        return "An unexpected error occurred. Please try again or contact support."
    
    # Return full error message for debugging
    return f"{type(exception).__name__}: {str(exception)}"


def log_error_with_context(
    exception: Exception,
    agent_name: Optional[str] = None,
    session_id: Optional[int] = None,
    user_id: Optional[int] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log error with full context information.
    
    Args:
        exception: The exception to log
        agent_name: Optional agent name
        session_id: Optional session ID
        user_id: Optional user ID
        additional_context: Optional additional context dictionary
    """
    context = {
        "agent_name": agent_name,
        "session_id": session_id,
        "user_id": user_id,
    }
    
    if additional_context:
        context.update(additional_context)
    
    # Remove None values
    context = {k: v for k, v in context.items() if v is not None}
    
    error_logger.error(
        f"Error in {agent_name or 'unknown'} - {str(exception)}",
        exc_info=True,
        extra=context
    )


# Convenience function for safe execution with error handling
def safe_execute(
    func: Callable[[], Any],
    fallback_value: Any = None,
    context: Optional[Dict[str, Any]] = None,
    log_errors: bool = True
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        fallback_value: Value to return if function fails
        context: Optional context for error logging
        log_errors: Whether to log errors (default: True)
        
    Returns:
        Function result or fallback_value if error occurs
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            log_error_with_context(e, additional_context=context)
        return fallback_value

