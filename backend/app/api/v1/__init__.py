"""
API v1 package initialization.
Exports all API v1 routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, memory_profiles, sessions, chat


# Create API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(memory_profiles.router)
api_router.include_router(sessions.router)
api_router.include_router(chat.router)

