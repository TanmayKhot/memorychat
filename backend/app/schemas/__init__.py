"""
Schemas package.
Exports all Pydantic schemas for API validation.
"""

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserLogin,
    TokenResponse,
)

from app.schemas.memory import (
    MemoryProfileCreate,
    MemoryProfileUpdate,
    MemoryProfileResponse,
    MemoryResponse,
    MemoryCreate,
    MemorySearchRequest,
    MemorySearchResponse,
)

from app.schemas.chat import (
    PrivacyMode,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionUpdate,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
    ConversationSummary,
    ErrorResponse,
)


__all__ = [
    # User schemas
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserLogin",
    "TokenResponse",
    # Memory schemas
    "MemoryProfileCreate",
    "MemoryProfileUpdate",
    "MemoryProfileResponse",
    "MemoryResponse",
    "MemoryCreate",
    "MemorySearchRequest",
    "MemorySearchResponse",
    # Chat schemas
    "PrivacyMode",
    "ChatSessionCreate",
    "ChatSessionResponse",
    "ChatSessionUpdate",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatRequest",
    "ChatResponse",
    "ChatStreamChunk",
    "ConversationSummary",
    "ErrorResponse",
]
