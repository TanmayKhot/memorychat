"""
Chat endpoints for MemoryChat Multi-Agent API.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database.database import get_db
from services.database_service import DatabaseService
from services.chat_service import ChatService
from models.api_models import (
    SendMessageRequest,
    ChatResponse,
    MessageResponse,
    MessageRole
)

router = APIRouter()


@router.post(
    "/chat/message",
    response_model=ChatResponse,
    summary="Send a chat message",
    description="""
    Send a message in a chat session. This endpoint processes the message through the multi-agent system:
    
    1. **Privacy Check**: Validates privacy mode and detects sensitive information
    2. **Memory Retrieval**: Retrieves relevant memories (if not in incognito mode)
    3. **Conversation Generation**: Generates contextual response using retrieved memories
    4. **Memory Storage**: Extracts and stores new memories (only in normal mode)
    5. **Analysis**: Performs periodic conversation analysis
    
    The response includes:
    - Assistant's message
    - Number of memories used in context
    - Number of new memories created
    - Privacy warnings (if any)
    - Metadata (tokens used, execution time, agents executed)
    
    **Privacy Modes:**
    - `normal`: Full memory storage and retrieval
    - `incognito`: No memory storage or retrieval
    - `pause_memory`: Memory retrieval only, no new storage
    """,
    response_description="Assistant response with metadata about memory usage and agent execution",
    responses={
        200: {
            "description": "Message processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Hello! How can I help you today?",
                        "memories_used": 3,
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
                    }
                }
            }
        },
        404: {"description": "Session not found"},
        400: {"description": "Invalid request"},
        500: {"description": "Internal server error"}
    }
)
async def send_message(
    request: SendMessageRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Send a chat message and receive an AI response.
    
    This is the main interaction endpoint. It processes your message through the
    multi-agent orchestration system and returns a contextual response.
    
    **Request Body:**
    - `session_id` (int): The chat session ID
    - `message` (str): Your message (minimum 1 character)
    
    **Response:**
    - `message` (str): The assistant's response
    - `memories_used` (int): Number of memories used in context
    - `new_memories_created` (int): Number of new memories created
    - `warnings` (list): Privacy or other warnings
    - `metadata` (dict): Execution metadata including tokens and timing
    
    **Example Request:**
    ```json
    {
        "session_id": 1,
        "message": "Hello! My name is Alice and I love Python programming."
    }
    ```
    
    **Example Response:**
    ```json
    {
        "message": "Hello Alice! It's great to meet you. I'd be happy to help with Python programming!",
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
    }
    ```
    """
    # Verify session exists
    db_service = DatabaseService(db)
    session = db_service.get_session_by_id(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {request.session_id} not found"
        )
    
    try:
        # Use ChatService to process message
        chat_service = ChatService(db)
        result = chat_service.process_message(
            session_id=request.session_id,
            user_message=request.message
        )
        
        return ChatResponse(
            message=result["message"],
            memories_used=result["memories_used"],
            new_memories_created=result["new_memories_created"],
            warnings=result["warnings"],
            metadata=result["metadata"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=List[MessageResponse],
    summary="Get session messages",
    description="Retrieve all messages in a chat session with pagination support.",
    response_description="List of messages in the session",
    responses={
        200: {"description": "Messages retrieved successfully"},
        404: {"description": "Session not found"}
    }
)
async def get_session_messages(
    session_id: int = ...,
    page: int = Query(1, ge=1, description="Page number (1-indexed)", example=1),
    limit: int = Query(50, ge=1, le=100, description="Number of items per page (max 100)", example=50),
    db: Session = Depends(get_db)
):
    """
    Get all messages in a chat session.
    
    **Parameters:**
    - `session_id` (path): The chat session ID
    - `page` (query): Page number, starting from 1
    - `limit` (query): Number of messages per page (1-100)
    
    **Returns:**
    List of messages ordered by creation time (oldest first).
    
    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "role": "user",
            "content": "Hello!",
            "created_at": "2024-01-01T12:00:00",
            "agent_name": null
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "Hello! How can I help you?",
            "created_at": "2024-01-01T12:00:05",
            "agent_name": "ContextCoordinatorAgent"
        }
    ]
    ```
    """
    db_service = DatabaseService(db)
    
    # Verify session exists
    session = db_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    try:
        messages = db_service.get_messages_by_session(session_id)
        
        # Simple pagination
        start_idx = (page - 1) * limit
        paginated_messages = messages[start_idx:start_idx + limit]
        
        return [
            MessageResponse(
                id=msg.id,
                role=MessageRole(msg.role),
                content=msg.content,
                created_at=msg.created_at,
                agent_name=msg.agent_name
            )
            for msg in paginated_messages
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/context",
    summary="Get session context",
    description="Retrieve current session context including privacy mode, profile, and recent memories. Useful for debugging.",
    response_description="Session context information",
    responses={
        200: {"description": "Context retrieved successfully"},
        404: {"description": "Session not found"}
    }
)
async def get_session_context(
    session_id: int = ...,
    db: Session = Depends(get_db)
):
    """
    Get current session context for debugging purposes.
    
    **Parameters:**
    - `session_id` (path): The chat session ID
    
    **Returns:**
    Dictionary containing:
    - `session_id`: Session ID
    - `privacy_mode`: Current privacy mode
    - `profile`: Profile information (id, name)
    - `recent_messages_count`: Number of recent messages
    - `recent_memories_count`: Number of recent memories
    - `recent_memories`: List of recent memories (up to 5)
    
    **Example Response:**
    ```json
    {
        "session_id": 1,
        "privacy_mode": "normal",
        "profile": {
            "id": 1,
            "name": "Work Profile"
        },
        "recent_messages_count": 5,
        "recent_memories_count": 3,
        "recent_memories": [
            {
                "id": 1,
                "content": "User prefers Python",
                "importance_score": 0.7,
                "memory_type": "preference"
            }
        ]
    }
    ```
    """
    db_service = DatabaseService(db)
    
    session = db_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    try:
        # Get profile info
        profile = None
        if session.memory_profile_id:
            profile = db_service.get_memory_profile_by_id(session.memory_profile_id)
        
        # Get recent messages
        recent_messages = db_service.get_recent_messages(session_id, limit=5)
        
        # Get recent memories if profile exists
        recent_memories = []
        if profile:
            memories = db_service.get_memories_by_profile(profile.id)
            recent_memories = [
                {
                    "id": mem.id,
                    "content": mem.content,
                    "importance_score": mem.importance_score,
                    "memory_type": mem.memory_type
                }
                for mem in memories[:5]
            ]
        
        return {
            "session_id": session.id,
            "privacy_mode": session.privacy_mode,
            "profile": {
                "id": profile.id if profile else None,
                "name": profile.name if profile else None
            } if profile else None,
            "recent_messages_count": len(recent_messages),
            "recent_memories_count": len(recent_memories),
            "recent_memories": recent_memories
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session context: {str(e)}"
        )


@router.delete(
    "/sessions/{session_id}/messages",
    status_code=status.HTTP_200_OK,
    summary="Clear session messages",
    description="Delete all messages in a session. The session itself remains active.",
    response_description="Success message with count of deleted messages",
    responses={
        200: {"description": "Messages cleared successfully"},
        404: {"description": "Session not found"}
    }
)
async def clear_session_messages(
    session_id: int = ...,
    db: Session = Depends(get_db)
):
    """
    Clear all messages in a chat session.
    
    **Parameters:**
    - `session_id` (path): The chat session ID
    
    **Returns:**
    Dictionary with:
    - `message`: Success message
    - `messages_deleted`: Number of messages deleted
    
    **Note:** This operation cannot be undone. The session remains active but all conversation history is removed.
    
    **Example Response:**
    ```json
    {
        "message": "Cleared 10 messages from session 1",
        "messages_deleted": 10
    }
    ```
    """
    db_service = DatabaseService(db)
    
    session = db_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    try:
        count = db_service.delete_messages_by_session(session_id)
        return {
            "message": f"Cleared {count} messages from session {session_id}",
            "messages_deleted": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear messages: {str(e)}"
        )

