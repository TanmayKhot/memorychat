"""
User endpoints for MemoryChat Multi-Agent API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from services.database_service import DatabaseService
from models.api_models import CreateUserRequest, UserResponse

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    Returns:
        UserResponse: Created user data
    """
    db_service = DatabaseService(db)
    
    try:
        user = db_service.create_user(
            email=request.email,
            username=request.username
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user details by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        UserResponse: User data
    """
    db_service = DatabaseService(db)
    
    user = db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at
    )


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db)
):
    """
    Get all users (for demo purposes).
    
    Returns:
        List[UserResponse]: List of all users
    """
    db_service = DatabaseService(db)
    
    try:
        # Get all users (simple implementation - in production would use pagination)
        # Note: DatabaseService doesn't have get_all_users, so we query directly
        from database.models import User
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                created_at=user.created_at
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

