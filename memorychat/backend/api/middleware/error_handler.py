"""
FastAPI error handlers for comprehensive error handling.
Provides global exception handlers for all error types.
"""
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DatabaseError
from pydantic import ValidationError
from openai import OpenAIError, APIError, RateLimitError, APIConnectionError

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.error_handler import (
    MemoryChatException,
    ProfileNotFoundException,
    SessionNotFoundException,
    InvalidPrivacyModeException,
    MemoryLimitExceededException,
    TokenLimitExceededException,
    LLMException,
    DatabaseException,
    UserNotFoundException,
    ValidationException,
    error_logger,
    app_logger
)


def generate_request_id() -> str:
    """Generate a unique request ID for tracking."""
    return str(uuid.uuid4())


def sanitize_error_message(message: str, hide_sensitive: bool = True) -> str:
    """
    Sanitize error message to hide sensitive information.
    
    Args:
        message: Original error message
        hide_sensitive: Whether to hide sensitive information
        
    Returns:
        Sanitized error message
    """
    if not hide_sensitive:
        return message
    
    import re
    
    # Hide API keys (various formats)
    # Pattern: sk- followed by alphanumeric characters (OpenAI format)
    message = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-***', message)
    # Pattern: api_key=value or api-key: value
    message = re.sub(r'api[_-]?key["\s:=]+([a-zA-Z0-9\-_]{10,})', 'api_key=***', message, flags=re.IGNORECASE)
    # Pattern: "key": "value" where value looks like an API key
    message = re.sub(r'["\']key["\']\s*:\s*["\']([a-zA-Z0-9\-_]{20,})["\']', '"key": "***"', message, flags=re.IGNORECASE)
    
    # Hide database paths
    message = re.sub(r'/[\w/]+\.(db|sqlite)', '/***.db', message)
    
    # Hide email addresses (partially)
    message = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'***@\2', message)
    
    return message


def create_error_response(
    error: str,
    detail: str,
    error_code: str = "GENERAL_ERROR",
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    request_id: str = None,
    details: Dict[str, Any] = None,
    hide_sensitive: bool = True
) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        error: Error type or code
        detail: Error detail message
        error_code: Programmatic error code
        status_code: HTTP status code
        request_id: Optional request ID for tracking
        details: Optional additional error details
        hide_sensitive: Whether to hide sensitive information
        
    Returns:
        JSONResponse with error information
    """
    # Sanitize error messages
    error = sanitize_error_message(error, hide_sensitive)
    detail = sanitize_error_message(detail, hide_sensitive)
    
    response_data = {
        "error": error,
        "error_code": error_code,
        "detail": detail,
        "timestamp": datetime.now().isoformat(),
    }
    
    if request_id:
        response_data["request_id"] = request_id
    
    if details:
        # Sanitize details
        sanitized_details = {}
        for key, value in details.items():
            if isinstance(value, str):
                sanitized_details[key] = sanitize_error_message(value, hide_sensitive)
            else:
                sanitized_details[key] = value
        response_data["details"] = sanitized_details
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


# ============================================================================
# Exception Handlers
# ============================================================================

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException (404, 403, etc.)."""
    request_id = generate_request_id()
    
    # Log the error
    app_logger.warning(
        f"HTTPException: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return create_error_response(
        error=f"HTTP_{exc.status_code}",
        detail=exc.detail,
        error_code=f"HTTP_{exc.status_code}",
        status_code=exc.status_code,
        request_id=request_id
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic ValidationError."""
    request_id = generate_request_id()
    
    # Extract validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        errors.append({
            "field": field,
            "message": message,
            "type": error.get("type", "unknown")
        })
    
    # Log the error
    error_logger.warning(
        f"ValidationError: {len(errors)} validation errors",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return create_error_response(
        error="ValidationError",
        detail=f"Validation failed: {len(errors)} error(s)",
        error_code="VALIDATION_ERROR",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request_id=request_id,
        details={"validation_errors": errors}
    )


async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    request_id = generate_request_id()
    
    # Determine error type
    if isinstance(exc, IntegrityError):
        error_code = "DATABASE_INTEGRITY_ERROR"
        detail = "Database integrity constraint violated. This may be due to duplicate data or invalid references."
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, DatabaseError):
        error_code = "DATABASE_ERROR"
        detail = "A database error occurred. Please try again."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        error_code = "DATABASE_ERROR"
        detail = "A database error occurred. Please try again."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Log the error
    error_logger.error(
        f"DatabaseError: {type(exc).__name__} - {str(exc)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        }
    )
    
    return create_error_response(
        error="DatabaseError",
        detail=detail,
        error_code=error_code,
        status_code=status_code,
        request_id=request_id,
        details={"error_type": type(exc).__name__}
    )


async def llm_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle LLM/OpenAI API errors."""
    request_id = generate_request_id()
    
    # Determine error type
    if isinstance(exc, RateLimitError):
        error_code = "LLM_RATE_LIMIT_ERROR"
        detail = "Rate limit exceeded. Please wait a moment and try again."
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, APIConnectionError):
        error_code = "LLM_CONNECTION_ERROR"
        detail = "Unable to connect to AI service. Please check your internet connection and try again."
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, APIError):
        error_code = "LLM_API_ERROR"
        detail = "AI service error. Please try again."
        status_code = status.HTTP_502_BAD_GATEWAY
    else:
        error_code = "LLM_ERROR"
        detail = "An error occurred while processing your request with AI service."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Log the error
    error_logger.error(
        f"LLMError: {type(exc).__name__} - {str(exc)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        }
    )
    
    return create_error_response(
        error="LLMError",
        detail=detail,
        error_code=error_code,
        status_code=status_code,
        request_id=request_id,
        details={"error_type": type(exc).__name__}
    )


async def memorychat_exception_handler(request: Request, exc: MemoryChatException) -> JSONResponse:
    """Handle custom MemoryChat exceptions."""
    request_id = generate_request_id()
    
    # Map exception types to HTTP status codes
    status_code_map = {
        ProfileNotFoundException: status.HTTP_404_NOT_FOUND,
        SessionNotFoundException: status.HTTP_404_NOT_FOUND,
        UserNotFoundException: status.HTTP_404_NOT_FOUND,
        InvalidPrivacyModeException: status.HTTP_400_BAD_REQUEST,
        MemoryLimitExceededException: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        TokenLimitExceededException: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
        LLMException: status.HTTP_502_BAD_GATEWAY,
        DatabaseException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Log the error
    log_level = "warning" if status_code < 500 else "error"
    getattr(error_logger, log_level)(
        f"MemoryChatException: {exc.error_code} - {exc.message}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )
    
    return create_error_response(
        error=exc.error_code,
        detail=exc.message,
        error_code=exc.error_code,
        status_code=status_code,
        request_id=request_id,
        details=exc.details
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    request_id = generate_request_id()
    
    # Log the error
    error_logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        }
    )
    
    return create_error_response(
        error="InternalServerError",
        detail="An unexpected error occurred. Please try again or contact support.",
        error_code="INTERNAL_SERVER_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
        details={"exception_type": type(exc).__name__}
    )


def register_error_handlers(app):
    """
    Register all error handlers with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    # Register handlers in order of specificity (most specific first)
    app.add_exception_handler(MemoryChatException, memorychat_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
    app.add_exception_handler(OpenAIError, llm_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    app_logger.info("Error handlers registered successfully")

