"""
Memory schemas.
Pydantic models for memory profile and memory-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MemoryProfileCreate(BaseModel):
    """Schema for creating a new memory profile."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Profile name")
    description: Optional[str] = Field(None, max_length=500, description="Profile description")
    is_default: bool = Field(default=False, description="Whether this is the default profile")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Work",
                "description": "Work-related conversations and memories",
                "is_default": False
            }
        }
    }


class MemoryProfileUpdate(BaseModel):
    """Schema for updating a memory profile."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="New profile name")
    description: Optional[str] = Field(None, max_length=500, description="New profile description")
    is_default: Optional[bool] = Field(None, description="Set as default profile")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Personal Projects",
                "description": "Personal coding and hobby projects"
            }
        }
    }


class MemoryProfileResponse(BaseModel):
    """Schema for memory profile response."""
    
    id: str = Field(..., description="Profile UUID")
    user_id: str = Field(..., description="User UUID who owns this profile")
    name: str = Field(..., description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    is_default: bool = Field(..., description="Whether this is the default profile")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Profile last update timestamp")
    memory_count: Optional[int] = Field(None, description="Number of memories in this profile")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "profile-uuid-123",
                "user_id": "user-uuid-456",
                "name": "Work",
                "description": "Work-related conversations",
                "is_default": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "memory_count": 42
            }
        }
    }


class MemoryResponse(BaseModel):
    """Schema for individual memory response."""
    
    id: str = Field(..., description="Memory ID from mem0")
    memory: str = Field(..., description="Memory content/text")
    created_at: Optional[datetime] = Field(None, description="Memory creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Memory last update timestamp")
    user_id: Optional[str] = Field(None, description="User ID")
    metadata: Optional[dict] = Field(None, description="Additional memory metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "mem0-id-789",
                "memory": "User prefers Python over JavaScript",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "user_id": "user-uuid-456",
                "metadata": {"confidence": 0.95, "category": "preferences"}
            }
        }
    }


class MemoryCreate(BaseModel):
    """Schema for creating a memory manually."""
    
    content: str = Field(..., min_length=1, description="Memory content to store")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "User's favorite color is blue"
            }
        }
    }


class MemorySearchRequest(BaseModel):
    """Schema for searching memories."""
    
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of results")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "user preferences",
                "limit": 10
            }
        }
    }


class MemorySearchResponse(BaseModel):
    """Schema for memory search results."""
    
    memories: List[MemoryResponse] = Field(..., description="List of relevant memories")
    count: int = Field(..., description="Number of memories returned")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "memories": [
                    {
                        "id": "mem0-id-1",
                        "memory": "User prefers Python",
                        "created_at": "2024-01-15T10:30:00Z",
                        "metadata": {}
                    }
                ],
                "count": 1
            }
        }
    }
