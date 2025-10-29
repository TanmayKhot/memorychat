"""
Chat sessions endpoints.
Handles CRUD operations for chat sessions and messages.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.security import get_current_user, verify_user_access
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatMessageResponse,
    PrivacyMode
)
from app.services.supabase_service import supabase_service


# Create router
router = APIRouter(prefix="/sessions", tags=["Chat Sessions"])


@router.get("", response_model=List[ChatSessionResponse])
async def get_sessions(
    memory_profile_id: Optional[str] = Query(None, description="Filter by memory profile ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[ChatSessionResponse]:
    """
    Get all chat sessions for the current user.
    
    Retrieves all chat sessions belonging to the authenticated user with
    optional filtering by memory profile and pagination support.
    
    Args:
        memory_profile_id: Optional filter by memory profile UUID
        limit: Maximum number of sessions to return (1-100, default 50)
        offset: Number of sessions to skip for pagination (default 0)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        List of ChatSessionResponse objects
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 500 if retrieval fails
    """
    try:
        user_id = current_user["id"]
        
        # Get sessions from database
        sessions = await supabase_service.get_user_sessions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        # Filter by memory_profile_id if provided
        if memory_profile_id:
            sessions = [s for s in sessions if s.get("memory_profile_id") == memory_profile_id]
        
        # Convert to response models with message counts
        response_sessions = []
        for session in sessions:
            # Get message count for each session
            try:
                messages = await supabase_service.get_session_messages(
                    session_id=session["id"],
                    limit=1000  # Get all messages to count them
                )
                message_count = len(messages)
            except Exception as e:
                print(f"Error getting message count for session {session['id']}: {e}")
                message_count = 0
            
            response_sessions.append(
                ChatSessionResponse(
                    id=session["id"],
                    user_id=session["user_id"],
                    memory_profile_id=session.get("memory_profile_id"),
                    privacy_mode=session["privacy_mode"],
                    created_at=session["created_at"],
                    updated_at=session["updated_at"],
                    message_count=message_count
                )
            )
        
        return response_sessions
        
    except Exception as e:
        print(f"Error getting sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat sessions"
        )


@router.post("", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: ChatSessionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ChatSessionResponse:
    """
    Create a new chat session.
    
    Creates a new chat session for the current user with the specified
    memory profile and privacy mode. If no memory profile is provided,
    uses the user's default profile.
    
    Args:
        session_data: Session creation data (memory_profile_id, privacy_mode)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        ChatSessionResponse with created session information
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 404 if memory profile not found
        HTTPException: 403 if memory profile doesn't belong to user
        HTTPException: 500 if creation fails
    """
    try:
        user_id = current_user["id"]
        
        # Determine which memory profile to use
        memory_profile_id = session_data.memory_profile_id
        
        if memory_profile_id:
            # Verify the profile exists and belongs to the user
            profile = await supabase_service.get_memory_profile(memory_profile_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Memory profile not found"
                )
            verify_user_access(current_user, profile["user_id"])
        else:
            # Use default profile if none specified
            default_profile = await supabase_service.get_default_memory_profile(user_id)
            if default_profile:
                memory_profile_id = default_profile["id"]
            # If no default profile, memory_profile_id will be None (allowed for incognito)
        
        # Create the session
        created_session = await supabase_service.create_chat_session(
            user_id=user_id,
            profile_id=memory_profile_id,
            privacy_mode=session_data.privacy_mode.value
        )
        
        if not created_session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chat session"
            )
        
        return ChatSessionResponse(
            id=created_session["id"],
            user_id=created_session["user_id"],
            memory_profile_id=created_session.get("memory_profile_id"),
            privacy_mode=created_session["privacy_mode"],
            created_at=created_session["created_at"],
            updated_at=created_session["updated_at"],
            message_count=0  # New session has no messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )


@router.get("/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ChatSessionResponse:
    """
    Get a specific chat session by ID.
    
    Returns detailed information about a specific chat session, including
    the count of messages in the session.
    
    Args:
        session_id: Session UUID
        current_user: Current authenticated user (from dependency)
        
    Returns:
        ChatSessionResponse with session information
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if session doesn't belong to user
        HTTPException: 404 if session not found
        HTTPException: 500 if retrieval fails
    """
    try:
        # Get the session
        session = await supabase_service.get_chat_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Verify user has access to this session
        verify_user_access(current_user, session["user_id"])
        
        # Get message count for this session
        try:
            messages = await supabase_service.get_session_messages(
                session_id=session_id,
                limit=1000  # Get all messages to count them
            )
            message_count = len(messages)
        except Exception as e:
            print(f"Error getting message count: {e}")
            message_count = 0
        
        return ChatSessionResponse(
            id=session["id"],
            user_id=session["user_id"],
            memory_profile_id=session.get("memory_profile_id"),
            privacy_mode=session["privacy_mode"],
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat session"
        )


@router.put("/{session_id}", response_model=ChatSessionResponse)
async def update_session(
    session_id: str,
    update_data: ChatSessionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ChatSessionResponse:
    """
    Update a chat session.
    
    Updates the privacy mode and/or memory profile of a chat session.
    Useful for switching privacy modes mid-conversation or changing the
    active memory profile.
    
    Args:
        session_id: Session UUID
        update_data: Session update data (privacy_mode, memory_profile_id)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        ChatSessionResponse with updated session information
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if session doesn't belong to user
        HTTPException: 404 if session or memory profile not found
        HTTPException: 500 if update fails
    """
    try:
        # Get the session to verify ownership
        session = await supabase_service.get_chat_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Verify user has access to this session
        verify_user_access(current_user, session["user_id"])
        
        # Prepare update data
        update_dict = {}
        
        if update_data.privacy_mode is not None:
            update_dict["privacy_mode"] = update_data.privacy_mode.value
        
        if update_data.memory_profile_id is not None:
            # Verify the profile exists and belongs to the user
            profile = await supabase_service.get_memory_profile(update_data.memory_profile_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Memory profile not found"
                )
            verify_user_access(current_user, profile["user_id"])
            update_dict["memory_profile_id"] = update_data.memory_profile_id
        
        # Update the session
        updated_session = await supabase_service.update_chat_session(
            session_id,
            update_dict
        )
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update chat session"
            )
        
        # Get message count
        try:
            messages = await supabase_service.get_session_messages(
                session_id=session_id,
                limit=1000
            )
            message_count = len(messages)
        except Exception as e:
            print(f"Error getting message count: {e}")
            message_count = 0
        
        return ChatSessionResponse(
            id=updated_session["id"],
            user_id=updated_session["user_id"],
            memory_profile_id=updated_session.get("memory_profile_id"),
            privacy_mode=updated_session["privacy_mode"],
            created_at=updated_session["created_at"],
            updated_at=updated_session["updated_at"],
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat session"
        )


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
async def delete_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a chat session.
    
    Deletes a chat session and all its associated messages. This action
    cannot be undone.
    
    Args:
        session_id: Session UUID
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if session doesn't belong to user
        HTTPException: 404 if session not found
        HTTPException: 500 if deletion fails
    """
    try:
        # Get the session to verify ownership
        session = await supabase_service.get_chat_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Verify user has access to this session
        verify_user_access(current_user, session["user_id"])
        
        # Delete all messages in the session first (optional, cascade should handle this)
        try:
            await supabase_service.delete_session_messages(session_id)
        except Exception as e:
            print(f"Error deleting session messages: {e}")
            # Continue with session deletion even if message deletion fails
        
        # Delete the session (this will cascade delete messages)
        success = await supabase_service.delete_chat_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete chat session"
            )
        
        return {
            "message": "Chat session deleted successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )


@router.get("/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[ChatMessageResponse]:
    """
    Get all messages for a specific session.
    
    Returns all messages in a chat session with pagination support.
    Messages are ordered by creation time (oldest first).
    
    Args:
        session_id: Session UUID
        limit: Maximum number of messages to return (1-500, default 100)
        offset: Number of messages to skip for pagination (default 0)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        List of ChatMessageResponse objects
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if session doesn't belong to user
        HTTPException: 404 if session not found
        HTTPException: 500 if retrieval fails
    """
    try:
        # Get the session to verify ownership
        session = await supabase_service.get_chat_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Verify user has access to this session
        verify_user_access(current_user, session["user_id"])
        
        # Get messages from database
        messages = await supabase_service.get_session_messages(
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        # Convert to response models
        response_messages = []
        for msg in messages:
            response_messages.append(
                ChatMessageResponse(
                    id=msg["id"],
                    session_id=msg["session_id"],
                    role=msg["role"],
                    content=msg["content"],
                    created_at=msg["created_at"],
                    metadata=msg.get("metadata")
                )
            )
        
        return response_messages
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting session messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session messages"
        )
