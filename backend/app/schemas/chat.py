"""
Chat schemas.
Pydantic models for chat session and message-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PrivacyMode(str, Enum):
    """Privacy mode for chat sessions."""
    
    NORMAL = "normal"
    INCOGNITO = "incognito"
    PAUSE_MEMORIES = "pause_memories"


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    
    memory_profile_id: Optional[str] = Field(None, description="Memory profile UUID (uses default if not provided)")
    privacy_mode: PrivacyMode = Field(default=PrivacyMode.NORMAL, description="Privacy mode for this session")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "memory_profile_id": "profile-uuid-123",
                "privacy_mode": "normal"
            }
        }
    }


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""
    
    id: str = Field(..., description="Session UUID")
    user_id: str = Field(..., description="User UUID who owns this session")
    memory_profile_id: Optional[str] = Field(None, description="Memory profile UUID")
    privacy_mode: str = Field(..., description="Privacy mode (normal, incognito, pause_memories)")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Session last update timestamp")
    message_count: Optional[int] = Field(None, description="Number of messages in this session")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "session-uuid-789",
                "user_id": "user-uuid-456",
                "memory_profile_id": "profile-uuid-123",
                "privacy_mode": "normal",
                "created_at": "2024-01-20T14:00:00Z",
                "updated_at": "2024-01-20T15:30:00Z",
                "message_count": 12
            }
        }
    }


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session."""
    
    privacy_mode: Optional[PrivacyMode] = Field(None, description="New privacy mode")
    memory_profile_id: Optional[str] = Field(None, description="New memory profile UUID")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "privacy_mode": "incognito"
            }
        }
    }


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""
    
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., min_length=1, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "user",
                "content": "What's the weather like today?",
                "metadata": {}
            }
        }
    }


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    
    id: str = Field(..., description="Message UUID")
    session_id: str = Field(..., description="Session UUID this message belongs to")
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Message creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "message-uuid-111",
                "session_id": "session-uuid-789",
                "role": "assistant",
                "content": "I don't have access to real-time weather data, but I can help you find weather information!",
                "created_at": "2024-01-20T15:30:00Z",
                "metadata": {"model": "gpt-4o-mini", "tokens": 150}
            }
        }
    }


class ChatRequest(BaseModel):
    """Schema for sending a chat message."""
    
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    stream: bool = Field(default=False, description="Whether to stream the response")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Tell me about Python programming",
                "stream": False
            }
        }
    }


class ChatResponse(BaseModel):
    """Schema for chat response."""
    
    success: bool = Field(..., description="Whether the request was successful")
    content: str = Field(..., description="AI assistant response")
    session_id: str = Field(..., description="Session UUID")
    privacy_mode: str = Field(..., description="Current privacy mode")
    memories_used: int = Field(..., description="Number of memories used for context")
    memories_extracted: bool = Field(..., description="Whether new memories were extracted")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata (model, tokens, etc.)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "content": "Python is a high-level programming language...",
                "session_id": "session-uuid-789",
                "privacy_mode": "normal",
                "memories_used": 3,
                "memories_extracted": True,
                "metadata": {
                    "model": "gpt-4o-mini",
                    "tokens": {"total_tokens": 200}
                }
            }
        }
    }


class ChatStreamChunk(BaseModel):
    """Schema for streaming chat response chunks."""
    
    success: bool = Field(..., description="Whether the chunk is successful")
    type: str = Field(..., description="Chunk type (metadata, content, complete, error)")
    content: Optional[str] = Field(None, description="Content chunk")
    done: Optional[bool] = Field(None, description="Whether streaming is complete")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional chunk metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "type": "content",
                "content": "Python is ",
                "done": False
            }
        }
    }


class ConversationSummary(BaseModel):
    """Schema for conversation summary."""
    
    session_id: str = Field(..., description="Session UUID")
    total_messages: int = Field(..., description="Total number of messages")
    user_messages: int = Field(..., description="Number of user messages")
    assistant_messages: int = Field(..., description="Number of assistant messages")
    first_message_at: Optional[datetime] = Field(None, description="Timestamp of first message")
    last_message_at: Optional[datetime] = Field(None, description="Timestamp of last message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session-uuid-789",
                "total_messages": 24,
                "user_messages": 12,
                "assistant_messages": 12,
                "first_message_at": "2024-01-20T14:00:00Z",
                "last_message_at": "2024-01-20T15:30:00Z"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type/code")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": "Session not found",
                "error_type": "SessionNotFound",
                "detail": "The requested chat session does not exist"
            }
        }
    }
