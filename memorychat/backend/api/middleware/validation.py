"""
Validation middleware for API requests.
Validates resource ownership, privacy mode transitions, and resource limits.
"""
from typing import Optional, Callable
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database.database import get_db
from services.database_service import DatabaseService
from services.error_handler import (
    ProfileNotFoundException,
    SessionNotFoundException,
    InvalidPrivacyModeException,
    MemoryLimitExceededException,
    ValidationException,
    app_logger
)

# Resource limits
MAX_MEMORIES_PER_PROFILE = 10000
MAX_SESSIONS_PER_USER = 1000
MAX_MESSAGES_PER_SESSION = 10000


def validate_session_belongs_to_user(
    session_id: int,
    user_id: int,
    db: Session
) -> bool:
    """
    Validate that a session belongs to a specific user.
    
    Args:
        session_id: Session ID to validate
        user_id: User ID that should own the session
        db: Database session
        
    Returns:
        True if session belongs to user
        
    Raises:
        SessionNotFoundException: If session doesn't exist
        HTTPException: If session doesn't belong to user
    """
    db_service = DatabaseService(db)
    session = db_service.get_session_by_id(session_id)
    
    if not session:
        raise SessionNotFoundException(session_id)
    
    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Session {session_id} does not belong to user {user_id}"
        )
    
    return True


def validate_profile_belongs_to_user(
    profile_id: int,
    user_id: int,
    db: Session
) -> bool:
    """
    Validate that a memory profile belongs to a specific user.
    
    Args:
        profile_id: Profile ID to validate
        user_id: User ID that should own the profile
        db: Database session
        
    Returns:
        True if profile belongs to user
        
    Raises:
        ProfileNotFoundException: If profile doesn't exist
        HTTPException: If profile doesn't belong to user
    """
    db_service = DatabaseService(db)
    profile = db_service.get_memory_profile_by_id(profile_id)
    
    if not profile:
        raise ProfileNotFoundException(profile_id)
    
    if profile.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Profile {profile_id} does not belong to user {user_id}"
        )
    
    return True


def validate_privacy_mode_transition(
    current_mode: str,
    new_mode: str
) -> bool:
    """
    Validate privacy mode transition.
    
    Args:
        current_mode: Current privacy mode
        new_mode: New privacy mode to transition to
        
    Returns:
        True if transition is valid
        
    Raises:
        InvalidPrivacyModeException: If transition is invalid
    """
    valid_modes = ["normal", "incognito", "pause_memory"]
    
    if new_mode not in valid_modes:
        raise InvalidPrivacyModeException(new_mode, valid_modes)
    
    # All transitions are allowed, but log them for audit
    if current_mode != new_mode:
        app_logger.info(
            f"Privacy mode transition: {current_mode} -> {new_mode}",
            extra={"current_mode": current_mode, "new_mode": new_mode}
        )
    
    return True


def check_memory_limit(
    profile_id: int,
    db: Session,
    limit: int = MAX_MEMORIES_PER_PROFILE
) -> bool:
    """
    Check if memory limit has been reached for a profile.
    
    Args:
        profile_id: Profile ID to check
        db: Database session
        limit: Maximum number of memories allowed
        
    Returns:
        True if under limit
        
    Raises:
        MemoryLimitExceededException: If limit exceeded
    """
    db_service = DatabaseService(db)
    memories = db_service.get_memories_by_profile(profile_id)
    current_count = len(memories)
    
    if current_count >= limit:
        raise MemoryLimitExceededException(limit, current_count)
    
    return True


def check_session_limit(
    user_id: int,
    db: Session,
    limit: int = MAX_SESSIONS_PER_USER
) -> bool:
    """
    Check if session limit has been reached for a user.
    
    Args:
        user_id: User ID to check
        db: Database session
        limit: Maximum number of sessions allowed
        
    Returns:
        True if under limit
        
    Raises:
        HTTPException: If limit exceeded
    """
    db_service = DatabaseService(db)
    sessions = db_service.get_sessions_by_user(user_id, limit=limit + 1)
    current_count = len(sessions)
    
    if current_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Session limit exceeded. Maximum {limit} sessions allowed."
        )
    
    return True


def check_message_limit(
    session_id: int,
    db: Session,
    limit: int = MAX_MESSAGES_PER_SESSION
) -> bool:
    """
    Check if message limit has been reached for a session.
    
    Args:
        session_id: Session ID to check
        db: Database session
        limit: Maximum number of messages allowed
        
    Returns:
        True if under limit
        
    Raises:
        HTTPException: If limit exceeded
    """
    db_service = DatabaseService(db)
    messages = db_service.get_messages_by_session(session_id)
    current_count = len(messages)
    
    if current_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Message limit exceeded. Maximum {limit} messages per session allowed."
        )
    
    return True


# Dependency functions for use in endpoints
def get_validated_session(
    session_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Dependency to get and validate a session belongs to user.
    
    Usage:
        @router.get("/sessions/{session_id}")
        async def get_session(
            session_id: int,
            user_id: int,
            session = Depends(get_validated_session)
        ):
            ...
    """
    validate_session_belongs_to_user(session_id, user_id, db)
    db_service = DatabaseService(db)
    return db_service.get_session_by_id(session_id)


def get_validated_profile(
    profile_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Dependency to get and validate a profile belongs to user.
    
    Usage:
        @router.get("/profiles/{profile_id}")
        async def get_profile(
            profile_id: int,
            user_id: int,
            profile = Depends(get_validated_profile)
        ):
            ...
    """
    validate_profile_belongs_to_user(profile_id, user_id, db)
    db_service = DatabaseService(db)
    return db_service.get_memory_profile_by_id(profile_id)

