"""
Session endpoints for MemoryChat Multi-Agent API.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from services.database_service import DatabaseService
from models.api_models import (
    CreateSessionRequest,
    UpdatePrivacyModeRequest,
    SessionResponse,
    PrivacyMode
)

router = APIRouter()


@router.get("/users/{user_id}/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get all sessions for a user with pagination.
    
    Args:
        user_id: User ID
        page: Page number (1-indexed)
        limit: Items per page
        
    Returns:
        List[SessionResponse]: List of sessions
    """
    db_service = DatabaseService(db)
    
    # Verify user exists
    user = db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        # Get sessions (limit is handled by the service method)
        sessions = db_service.get_sessions_by_user(user_id, limit=limit * page)
        
        # Simple pagination (in production, use proper offset/limit)
        start_idx = (page - 1) * limit
        paginated_sessions = sessions[start_idx:start_idx + limit]
        
        result = []
        for session in paginated_sessions:
            # Get message count
            message_count = len(db_service.get_messages_by_session(session.id))
            
            result.append(SessionResponse(
                id=session.id,
                title=session.title,
                privacy_mode=PrivacyMode(session.privacy_mode),
                created_at=session.created_at,
                message_count=message_count
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.post("/users/{user_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    user_id: int,
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new chat session.
    
    Args:
        user_id: User ID
        request: Session creation data
        
    Returns:
        SessionResponse: Created session
    """
    db_service = DatabaseService(db)
    
    # Verify user exists
    user = db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Verify profile exists
    profile = db_service.get_memory_profile_by_id(request.memory_profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {request.memory_profile_id} not found"
        )
    
    # Verify profile belongs to user
    if profile.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile does not belong to this user"
        )
    
    try:
        session = db_service.create_session(
            user_id=user_id,
            memory_profile_id=request.memory_profile_id,
            privacy_mode=request.privacy_mode.value
        )
        
        return SessionResponse(
            id=session.id,
            title=session.title,
            privacy_mode=PrivacyMode(session.privacy_mode),
            created_at=session.created_at,
            message_count=0
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get session details including message count and recent messages.
    
    Args:
        session_id: Session ID
        
    Returns:
        SessionResponse: Session data
    """
    db_service = DatabaseService(db)
    
    session = db_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    try:
        # Get message count
        messages = db_service.get_messages_by_session(session_id)
        message_count = len(messages)
        
        return SessionResponse(
            id=session.id,
            title=session.title,
            privacy_mode=PrivacyMode(session.privacy_mode),
            created_at=session.created_at,
            message_count=message_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.put("/sessions/{session_id}/privacy-mode", response_model=SessionResponse)
async def update_privacy_mode(
    session_id: int,
    request: UpdatePrivacyModeRequest,
    db: Session = Depends(get_db)
):
    """
    Update privacy mode mid-conversation.
    
    Args:
        session_id: Session ID
        request: New privacy mode
        
    Returns:
        SessionResponse: Updated session
    """
    db_service = DatabaseService(db)
    
    session = db_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    try:
        # Log the change
        from config.logging_config import app_logger
        app_logger.info(
            f"Privacy mode changed for session {session_id}: "
            f"{session.privacy_mode} -> {request.privacy_mode.value}"
        )
        
        updated_session = db_service.update_session(
            session_id,
            privacy_mode=request.privacy_mode.value
        )
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )
        
        # Get message count
        messages = db_service.get_messages_by_session(session_id)
        message_count = len(messages)
        
        return SessionResponse(
            id=updated_session.id,
            title=updated_session.title,
            privacy_mode=PrivacyMode(updated_session.privacy_mode),
            created_at=updated_session.created_at,
            message_count=message_count
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update privacy mode: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a session and all messages.
    
    Args:
        session_id: Session ID
        
    Returns:
        dict: Success message
    """
    db_service = DatabaseService(db)
    
    session = db_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    try:
        success = db_service.delete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )
        
        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


