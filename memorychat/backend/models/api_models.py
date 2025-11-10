"""
Pydantic models for API request/response schemas.

This module defines all request and response models used by the FastAPI endpoints,
ensuring proper validation and serialization of API data.
"""
import re
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ============================================================================
# ENUMS
# ============================================================================

class PrivacyMode(str, Enum):
    """Privacy mode enum for chat sessions."""
    NORMAL = "normal"
    INCOGNITO = "incognito"
    PAUSE_MEMORY = "pause_memory"


class MessageRole(str, Enum):
    """Message role enum for chat messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MemoryType(str, Enum):
    """Memory type enum for categorizing memories."""
    FACT = "fact"
    PREFERENCE = "preference"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    OTHER = "other"


# ============================================================================
# REQUEST MODELS
# ============================================================================

class CreateUserRequest(BaseModel):
    """
    Request model for creating a new user.
    
    Creates a new user account in the system. Email must be unique.
    """
    email: EmailStr = Field(
        ...,
        description="User email address (must be unique)",
        examples=["user@example.com", "alice@company.com"]
    )
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Username (must be unique, 1-50 characters)",
        examples=["johndoe", "alice_smith"]
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username is not empty and doesn't contain SQL injection patterns."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        
        v = v.strip()
        
        # Check for SQL injection patterns
        sql_injection_patterns = [
            r"['\";].*DROP\s+TABLE",
            r"['\";].*DELETE\s+FROM",
            r"['\";].*UPDATE\s+.*SET",
            r"['\";].*INSERT\s+INTO",
            r"['\";].*ALTER\s+TABLE",
            r"['\";].*EXEC\s*\(",
            r"['\";].*EXECUTE\s*\(",
            r"['\";].*UNION\s+SELECT",
            r"['\";].*OR\s+['\"]?1['\"]?\s*=\s*['\"]?1",
            r"['\";].*--",
            r"['\";].*/\*",
            r"['\";].*\*/",
        ]
        
        for pattern in sql_injection_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Username contains invalid characters or patterns")
        
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "johndoe"
                },
                {
                    "email": "alice@company.com",
                    "username": "alice_smith"
                }
            ]
        }


class CreateMemoryProfileRequest(BaseModel):
    """
    Request model for creating a new memory profile.
    
    Memory profiles allow you to organize conversations with different personalities
    and contexts. Each profile maintains its own set of memories.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Profile name (must be unique per user, 1-100 characters)",
        examples=["Work Profile", "Personal", "Study Assistant"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional description of the profile's purpose",
        examples=["Professional conversations and work-related topics", "Personal assistant for daily tasks"]
    )
    system_prompt: Optional[str] = Field(
        None,
        max_length=2000,
        description="Custom system prompt to customize the assistant's personality and behavior",
        examples=[
            "You are a professional assistant focused on productivity and efficiency.",
            "You are a friendly and casual assistant for personal conversations."
        ]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty and doesn't contain SQL injection patterns."""
        if not v or not v.strip():
            raise ValueError("Profile name cannot be empty")
        
        v = v.strip()
        
        # Check for SQL injection patterns
        sql_injection_patterns = [
            r"['\";].*DROP\s+TABLE",
            r"['\";].*DELETE\s+FROM",
            r"['\";].*UPDATE\s+.*SET",
            r"['\";].*INSERT\s+INTO",
            r"['\";].*ALTER\s+TABLE",
            r"['\";].*EXEC\s*\(",
            r"['\";].*EXECUTE\s*\(",
            r"['\";].*UNION\s+SELECT",
            r"['\";].*OR\s+['\"]?1['\"]?\s*=\s*['\"]?1",
            r"['\";].*--",
            r"['\";].*/\*",
            r"['\";].*\*/",
        ]
        
        for pattern in sql_injection_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Profile name contains invalid characters or patterns")
        
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Work Profile",
                    "description": "Professional conversations",
                    "system_prompt": "You are a professional assistant focused on productivity."
                },
                {
                    "name": "Personal",
                    "description": "Personal assistant for daily tasks",
                    "system_prompt": "You are a friendly and helpful personal assistant."
                }
            ]
        }


class UpdateMemoryProfileRequest(BaseModel):
    """Request model for updating an existing memory profile."""
    name: Optional[str] = Field(None, min_length=1, description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    is_default: Optional[bool] = Field(None, description="Whether this is the default profile")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name is not empty if provided and doesn't contain SQL injection patterns."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Profile name cannot be empty")
        
        if v is None:
            return None
        
        v = v.strip()
        
        # Check for SQL injection patterns
        sql_injection_patterns = [
            r"['\";].*DROP\s+TABLE",
            r"['\";].*DELETE\s+FROM",
            r"['\";].*UPDATE\s+.*SET",
            r"['\";].*INSERT\s+INTO",
            r"['\";].*ALTER\s+TABLE",
            r"['\";].*EXEC\s*\(",
            r"['\";].*EXECUTE\s*\(",
            r"['\";].*UNION\s+SELECT",
            r"['\";].*OR\s+['\"]?1['\"]?\s*=\s*['\"]?1",
            r"['\";].*--",
            r"['\";].*/\*",
            r"['\";].*\*/",
        ]
        
        for pattern in sql_injection_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Profile name contains invalid characters or patterns")
        
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Work Profile",
                "description": "Updated description",
                "system_prompt": "Updated prompt",
                "is_default": True
            }
        }


class CreateSessionRequest(BaseModel):
    """Request model for creating a new chat session."""
    memory_profile_id: int = Field(..., gt=0, description="Memory profile ID to use")
    privacy_mode: PrivacyMode = Field(PrivacyMode.NORMAL, description="Privacy mode for the session")

    class Config:
        json_schema_extra = {
            "example": {
                "memory_profile_id": 1,
                "privacy_mode": "normal"
            }
        }


class SendMessageRequest(BaseModel):
    """
    Request model for sending a message in a chat session.
    
    Send a message to the AI assistant. The message will be processed through
    the multi-agent system and a contextual response will be returned.
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Your message to the assistant (1-10,000 characters)",
        examples=[
            "Hello! How are you?",
            "What programming languages do you know?",
            "Remember that I prefer dark mode interfaces."
        ]
    )
    session_id: int = Field(
        ...,
        gt=0,
        description="The chat session ID where this message belongs",
        examples=[1, 2, 3]
    )

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Hello, how are you?",
                    "session_id": 1
                },
                {
                    "message": "My name is Alice and I love Python programming.",
                    "session_id": 1
                }
            ]
        }


class UpdatePrivacyModeRequest(BaseModel):
    """Request model for updating privacy mode of a session."""
    privacy_mode: PrivacyMode = Field(..., description="New privacy mode")

    class Config:
        json_schema_extra = {
            "example": {
                "privacy_mode": "incognito"
            }
        }


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class UserResponse(BaseModel):
    """Response model for user data."""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class MemoryProfileResponse(BaseModel):
    """Response model for memory profile data."""
    id: int = Field(..., description="Profile ID")
    name: str = Field(..., description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    is_default: bool = Field(..., description="Whether this is the default profile")
    created_at: datetime = Field(..., description="Profile creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Work Profile",
                "description": "Professional conversations",
                "is_default": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class SessionResponse(BaseModel):
    """Response model for chat session data."""
    id: int = Field(..., description="Session ID")
    title: Optional[str] = Field(None, description="Session title")
    privacy_mode: PrivacyMode = Field(..., description="Privacy mode")
    created_at: datetime = Field(..., description="Session creation timestamp")
    message_count: int = Field(..., ge=0, description="Number of messages in session")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Chat Session 1",
                "privacy_mode": "normal",
                "created_at": "2024-01-01T00:00:00",
                "message_count": 5
            }
        }


class MessageResponse(BaseModel):
    """Response model for chat message data."""
    id: int = Field(..., description="Message ID")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Message creation timestamp")
    agent_name: Optional[str] = Field(None, description="Agent that generated this message")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "role": "assistant",
                "content": "Hello! How can I help you?",
                "created_at": "2024-01-01T00:00:00",
                "agent_name": "ConversationAgent"
            }
        }


class ChatResponse(BaseModel):
    """
    Response model for chat message endpoint.
    
    Contains the assistant's response along with metadata about memory usage
    and agent execution.
    """
    message: str = Field(
        ...,
        description="The assistant's response message",
        examples=["Hello! How can I help you today?", "I remember you prefer Python programming!"]
    )
    memories_used: int = Field(
        ...,
        ge=0,
        description="Number of memories retrieved and used in the conversation context",
        examples=[0, 3, 5]
    )
    new_memories_created: int = Field(
        ...,
        ge=0,
        description="Number of new memories extracted and stored from this conversation",
        examples=[0, 1, 2]
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of privacy warnings or other important notices",
        examples=[[], ["Sensitive information detected"], ["Memory limit approaching"]]
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the request processing",
        examples=[
            {
                "tokens_used": 150,
                "execution_time_ms": 1200,
                "agents_executed": ["PrivacyGuardianAgent", "ConversationAgent"],
                "privacy_mode": "normal"
            }
        ]
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Hello! How can I help you today?",
                    "memories_used": 0,
                    "new_memories_created": 1,
                    "warnings": [],
                    "metadata": {
                        "tokens_used": 150,
                        "execution_time_ms": 1200,
                        "agents_executed": ["PrivacyGuardianAgent", "MemoryRetrievalAgent", "ConversationAgent", "MemoryManagerAgent"],
                        "tokens_by_agent": {"ConversationAgent": 100},
                        "privacy_mode": "normal",
                        "profile_id": 1
                    }
                },
                {
                    "message": "I remember you prefer Python programming! How can I help you with Python today?",
                    "memories_used": 2,
                    "new_memories_created": 0,
                    "warnings": [],
                    "metadata": {
                        "tokens_used": 200,
                        "execution_time_ms": 1500,
                        "agents_executed": ["PrivacyGuardianAgent", "MemoryRetrievalAgent", "ConversationAgent"],
                        "privacy_mode": "pause_memory",
                        "profile_id": 1
                    }
                }
            ]
        }


class MemoryResponse(BaseModel):
    """Response model for memory data."""
    id: int = Field(..., description="Memory ID")
    content: str = Field(..., description="Memory content")
    importance_score: float = Field(..., ge=0.0, le=1.0, description="Importance score (0.0 to 1.0)")
    memory_type: Optional[MemoryType] = Field(None, description="Memory type")
    tags: Optional[List[str]] = Field(None, description="Memory tags")
    created_at: datetime = Field(..., description="Memory creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "content": "User prefers dark mode",
                "importance_score": 0.7,
                "memory_type": "preference",
                "tags": ["ui", "preference"],
                "created_at": "2024-01-01T00:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    error: str = Field(..., description="Error type or code")
    detail: str = Field(..., description="Error detail message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "detail": "Invalid email format",
                "timestamp": "2024-01-01T00:00:00"
            }
        }

