"""
FastAPI application entry point for MemoryChat Multi-Agent application.
"""
import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config.logging_config import app_logger
from database.database import init_db
from models.api_models import ErrorResponse


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    app_logger.info("Starting MemoryChat Multi-Agent API...")
    try:
        init_db()
        app_logger.info("Database initialized successfully")
    except Exception as e:
        app_logger.error(f"Failed to initialize database: {str(e)}")
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down MemoryChat Multi-Agent API...")


# Create FastAPI application with comprehensive documentation
app = FastAPI(
    title="MemoryChat Multi-Agent API",
    description="""
    ## MemoryChat Multi-Agent API
    
    A comprehensive API for managing conversational AI with persistent memory, privacy controls, and multi-agent orchestration.
    
    ### Features
    
    * **User Management**: Create and manage users
    * **Memory Profiles**: Organize conversations with different personality profiles
    * **Chat Sessions**: Manage multiple conversation sessions
    * **Memory Management**: Store and retrieve contextual memories
    * **Privacy Controls**: Normal, Incognito, and Pause Memory modes
    * **Multi-Agent System**: Coordinated AI agents for conversation, memory, privacy, and analysis
    
    ### Privacy Modes
    
    * **normal**: Full memory storage and retrieval
    * **incognito**: No memory storage or retrieval
    * **pause_memory**: Memory retrieval only, no new storage
    
    ### Authentication
    
    Currently, the API uses user IDs for resource access. In production, implement proper authentication.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "users",
            "description": "User management operations. Create and retrieve users.",
        },
        {
            "name": "memory-profiles",
            "description": "Memory profile management. Create profiles with different personalities and system prompts.",
        },
        {
            "name": "sessions",
            "description": "Chat session management. Create and manage conversation sessions with privacy controls.",
        },
        {
            "name": "chat",
            "description": "Chat operations. Send messages and interact with the multi-agent system.",
        },
        {
            "name": "memories",
            "description": "Memory management. View, search, and manage stored memories.",
        },
        {
            "name": "analytics",
            "description": "Analytics and insights. Get conversation analytics and profile statistics.",
        },
    ],
    contact={
        "name": "MemoryChat API Support",
        "email": "support@memorychat.example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8000", 
        "http://localhost:8080",
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "null"  # Allow file:// protocol
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests."""
    start_time = time.time()
    
    # Log request
    app_logger.info(f"{request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    app_logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


# Register error handlers from middleware
from api.middleware.error_handler import register_error_handlers
register_error_handlers(app)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {"message": "MemoryChat Multi-Agent API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "MemoryChat Multi-Agent API"}


# Include routers
from api.endpoints import users, memory_profiles, sessions, chat, memories, analytics

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(memory_profiles.router, prefix="/api", tags=["memory-profiles"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(memories.router, prefix="/api", tags=["memories"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )

