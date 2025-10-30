"""
FastAPI application entry point.
Main application file for the MemoryChat backend.

Checkpoint 3.13: Main Application
- Initialize FastAPI app
- Add CORS middleware
- Include all API routers
- Add global exception handlers
- Add startup/shutdown events
- Configure OpenAPI documentation
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.security import get_cors_config
from app.api.v1 import api_router


# =============================================================================
# Lifespan Event Handler (Startup/Shutdown)
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan event handler.
    Handles startup and shutdown events using modern async context manager pattern.
    
    Startup tasks:
    - Initialize connections
    - Load configurations
    - Print startup information
    
    Shutdown tasks:
    - Close connections
    - Cleanup resources
    """
    # Startup
    print("=" * 70)
    print(f"🚀 Starting {settings.APP_NAME}")
    print("=" * 70)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"API Version: 1.0.0")
    print(f"API v1 Prefix: {settings.API_V1_PREFIX}")
    print(f"Documentation: {settings.API_V1_PREFIX}/docs")
    print("=" * 70)
    
    # Initialize services here if needed
    # e.g., database connections, cache connections, etc.
    
    yield
    
    # Shutdown
    print("=" * 70)
    print(f"🛑 Shutting down {settings.APP_NAME}")
    print("=" * 70)
    
    # Cleanup resources here if needed
    # e.g., close database connections, flush caches, etc.


# =============================================================================
# Initialize FastAPI Application
# =============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "MemoryChat API - AI chat platform with switchable memory profiles\n\n"
        "Features:\n"
        "- User authentication and authorization\n"
        "- Multiple memory profiles per user\n"
        "- Chat sessions with privacy modes (normal, incognito, pause_memories)\n"
        "- AI-powered conversations with memory context\n"
        "- Streaming chat support (Server-Sent Events)\n"
        "- Memory extraction and semantic search"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "MemoryChat Support",
        "email": "support@memorychat.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Root",
            "description": "Root and health check endpoints",
        },
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints",
        },
        {
            "name": "Memory Profiles",
            "description": "Memory profile management endpoints",
        },
        {
            "name": "Chat Sessions",
            "description": "Chat session management endpoints",
        },
        {
            "name": "Chat",
            "description": "Chat messaging endpoints (standard and streaming)",
        },
    ],
)


# =============================================================================
# CORS Middleware Configuration
# =============================================================================
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)


# =============================================================================
# Include API Routers
# =============================================================================
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# =============================================================================
# Root Endpoints
# =============================================================================
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    
    Returns basic information about the API including status and documentation links.
    """
    return {
        "message": "MemoryChat API",
        "status": "running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "api": {
            "v1": settings.API_V1_PREFIX
        }
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the application.
    Used by monitoring systems and load balancers.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


# =============================================================================
# Global Exception Handlers
# =============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions (4xx, 5xx status codes).
    
    Returns a JSON response with error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors (422 status code).
    
    Returns detailed validation error information.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Catches all unhandled exceptions and returns a generic error response.
    In development mode, includes the exception message for debugging.
    """
    # Log the exception (in production, use proper logging)
    print(f"❌ Unhandled exception: {exc}")
    print(f"   Request: {request.method} {request.url}")
    
    # Return appropriate response based on environment
    if settings.ENVIRONMENT == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__,
                "path": str(request.url)
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
                "path": str(request.url)
            }
        )


# =============================================================================
# Application Entry Point
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )
