"""
Memory profile endpoints for MemoryChat Multi-Agent API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from services.database_service import DatabaseService
from models.api_models import (
    CreateMemoryProfileRequest,
    UpdateMemoryProfileRequest,
    MemoryProfileResponse
)

router = APIRouter()


@router.get("/users/{user_id}/profiles", response_model=List[MemoryProfileResponse])
async def get_user_profiles(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all memory profiles for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List[MemoryProfileResponse]: List of memory profiles
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
        profiles = db_service.get_memory_profiles_by_user(user_id)
        return [
            MemoryProfileResponse(
                id=profile.id,
                name=profile.name,
                description=profile.description,
                is_default=bool(profile.is_default),
                created_at=profile.created_at
            )
            for profile in profiles
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profiles: {str(e)}"
        )


@router.post("/users/{user_id}/profiles", response_model=MemoryProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_profile(
    user_id: int,
    request: CreateMemoryProfileRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new memory profile for a user.
    Sets as default if it's the first profile.
    
    Args:
        user_id: User ID
        request: Profile creation data
        
    Returns:
        MemoryProfileResponse: Created profile
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
        # Check if this is the first profile
        existing_profiles = db_service.get_memory_profiles_by_user(user_id)
        is_default = len(existing_profiles) == 0
        
        profile = db_service.create_memory_profile(
            user_id=user_id,
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            is_default=is_default
        )
        
        return MemoryProfileResponse(
            id=profile.id,
            name=profile.name,
            description=profile.description,
            is_default=bool(profile.is_default),
            created_at=profile.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.get("/profiles/{profile_id}", response_model=MemoryProfileResponse)
async def get_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific profile details with memory count.
    
    Args:
        profile_id: Profile ID
        
    Returns:
        MemoryProfileResponse: Profile data
    """
    db_service = DatabaseService(db)
    
    profile = db_service.get_memory_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    return MemoryProfileResponse(
        id=profile.id,
        name=profile.name,
        description=profile.description,
        is_default=bool(profile.is_default),
        created_at=profile.created_at
    )


@router.put("/profiles/{profile_id}", response_model=MemoryProfileResponse)
async def update_profile(
    profile_id: int,
    request: UpdateMemoryProfileRequest,
    db: Session = Depends(get_db)
):
    """
    Update profile details.
    
    Args:
        profile_id: Profile ID
        request: Update data
        
    Returns:
        MemoryProfileResponse: Updated profile
    """
    db_service = DatabaseService(db)
    
    profile = db_service.get_memory_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    try:
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.description is not None:
            update_data["description"] = request.description
        if request.system_prompt is not None:
            update_data["system_prompt"] = request.system_prompt
        if request.is_default is not None:
            update_data["is_default"] = request.is_default
        
        updated_profile = db_service.update_memory_profile(profile_id, **update_data)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with ID {profile_id} not found"
            )
        
        return MemoryProfileResponse(
            id=updated_profile.id,
            name=updated_profile.name,
            description=updated_profile.description,
            is_default=bool(updated_profile.is_default),
            created_at=updated_profile.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a memory profile and all associated memories.
    Cannot delete if it's the only profile.
    
    Args:
        profile_id: Profile ID
        
    Returns:
        dict: Success message
    """
    db_service = DatabaseService(db)
    
    profile = db_service.get_memory_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    try:
        success = db_service.delete_memory_profile(profile_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the only memory profile for a user"
            )
        
        return {"message": f"Profile {profile_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )


@router.post("/profiles/{profile_id}/set-default", status_code=status.HTTP_200_OK)
async def set_default_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """
    Set a profile as default and unset previous default.
    
    Args:
        profile_id: Profile ID
        
    Returns:
        dict: Success message
    """
    db_service = DatabaseService(db)
    
    profile = db_service.get_memory_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    try:
        updated_profile = db_service.set_default_profile(profile_id, profile.user_id)
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to set default profile"
            )
        
        return {"message": f"Profile {profile_id} set as default successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default profile: {str(e)}"
        )


