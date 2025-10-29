"""
Memory profiles endpoints.
Handles CRUD operations for memory profiles.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.security import get_current_user, verify_user_access
from app.schemas.memory import (
    MemoryProfileCreate,
    MemoryProfileUpdate,
    MemoryProfileResponse,
    MemoryResponse
)
from app.services.supabase_service import supabase_service
from app.services.mem0_service import mem0_service


# Create router
router = APIRouter(prefix="/memory-profiles", tags=["Memory Profiles"])


@router.get("", response_model=List[MemoryProfileResponse])
async def get_memory_profiles(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[MemoryProfileResponse]:
    """
    Get all memory profiles for the current user.
    
    Returns a list of all memory profiles belonging to the authenticated user,
    ordered by creation date.
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        List of MemoryProfileResponse objects
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 500 if retrieval fails
    """
    try:
        user_id = current_user["id"]
        
        # Get all profiles for this user
        profiles = await supabase_service.get_memory_profiles(user_id)
        
        # Convert to response models
        response_profiles = []
        for profile in profiles:
            # Get memory count for each profile
            try:
                memories = await mem0_service.get_memories(user_id, profile["id"])
                memory_count = len(memories)
            except Exception as e:
                print(f"Error getting memory count for profile {profile['id']}: {e}")
                memory_count = 0
            
            response_profiles.append(
                MemoryProfileResponse(
                    id=profile["id"],
                    user_id=profile["user_id"],
                    name=profile["name"],
                    description=profile.get("description"),
                    is_default=profile["is_default"],
                    created_at=profile["created_at"],
                    updated_at=profile["updated_at"],
                    memory_count=memory_count
                )
            )
        
        return response_profiles
        
    except Exception as e:
        print(f"Error getting memory profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memory profiles"
        )


@router.post("", response_model=MemoryProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_profile(
    profile_data: MemoryProfileCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> MemoryProfileResponse:
    """
    Create a new memory profile.
    
    Creates a new memory profile for the current user. If this is the user's
    first profile, it will automatically be set as the default profile.
    
    Args:
        profile_data: Profile creation data (name, description, is_default)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        MemoryProfileResponse with created profile information
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 400 if profile with same name exists
        HTTPException: 500 if creation fails
    """
    try:
        user_id = current_user["id"]
        
        # Check if user already has profiles
        existing_profiles = await supabase_service.get_memory_profiles(user_id)
        
        # If this is the first profile, force it to be default
        is_default = profile_data.is_default
        if len(existing_profiles) == 0:
            is_default = True
        
        # Create the profile
        created_profile = await supabase_service.create_memory_profile(
            user_id=user_id,
            name=profile_data.name,
            description=profile_data.description,
            is_default=is_default
        )
        
        if not created_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create memory profile"
            )
        
        return MemoryProfileResponse(
            id=created_profile["id"],
            user_id=created_profile["user_id"],
            name=created_profile["name"],
            description=created_profile.get("description"),
            is_default=created_profile["is_default"],
            created_at=created_profile["created_at"],
            updated_at=created_profile["updated_at"],
            memory_count=0  # New profile has no memories
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating memory profile: {e}")
        # Check if it's a unique constraint violation
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A profile with the name '{profile_data.name}' already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create memory profile"
        )


@router.get("/{profile_id}", response_model=MemoryProfileResponse)
async def get_memory_profile(
    profile_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> MemoryProfileResponse:
    """
    Get a specific memory profile by ID.
    
    Returns detailed information about a specific memory profile, including
    the count of memories stored in it.
    
    Args:
        profile_id: Profile UUID
        current_user: Current authenticated user (from dependency)
        
    Returns:
        MemoryProfileResponse with profile information
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if profile doesn't belong to user
        HTTPException: 404 if profile not found
        HTTPException: 500 if retrieval fails
    """
    try:
        # Get the profile
        profile = await supabase_service.get_memory_profile(profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory profile not found"
            )
        
        # Verify user has access to this profile
        verify_user_access(current_user, profile["user_id"])
        
        # Get memory count for this profile
        try:
            memories = await mem0_service.get_memories(
                current_user["id"],
                profile_id
            )
            memory_count = len(memories)
        except Exception as e:
            print(f"Error getting memory count: {e}")
            memory_count = 0
        
        return MemoryProfileResponse(
            id=profile["id"],
            user_id=profile["user_id"],
            name=profile["name"],
            description=profile.get("description"),
            is_default=profile["is_default"],
            created_at=profile["created_at"],
            updated_at=profile["updated_at"],
            memory_count=memory_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting memory profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memory profile"
        )


@router.put("/{profile_id}", response_model=MemoryProfileResponse)
async def update_memory_profile(
    profile_id: str,
    update_data: MemoryProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> MemoryProfileResponse:
    """
    Update a memory profile.
    
    Updates the name and/or description of a memory profile. Can also set
    the profile as default.
    
    Args:
        profile_id: Profile UUID
        update_data: Profile update data (name, description, is_default)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        MemoryProfileResponse with updated profile information
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if profile doesn't belong to user
        HTTPException: 404 if profile not found
        HTTPException: 400 if profile name already exists
        HTTPException: 500 if update fails
    """
    try:
        # Get the profile to verify ownership
        profile = await supabase_service.get_memory_profile(profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory profile not found"
            )
        
        # Verify user has access to this profile
        verify_user_access(current_user, profile["user_id"])
        
        # Prepare update data (only include fields that are provided)
        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.description is not None:
            update_dict["description"] = update_data.description
        if update_data.is_default is not None:
            update_dict["is_default"] = update_data.is_default
        
        # Update the profile
        updated_profile = await supabase_service.update_memory_profile(
            profile_id,
            update_dict
        )
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update memory profile"
            )
        
        # Get memory count
        try:
            memories = await mem0_service.get_memories(
                current_user["id"],
                profile_id
            )
            memory_count = len(memories)
        except Exception as e:
            print(f"Error getting memory count: {e}")
            memory_count = 0
        
        return MemoryProfileResponse(
            id=updated_profile["id"],
            user_id=updated_profile["user_id"],
            name=updated_profile["name"],
            description=updated_profile.get("description"),
            is_default=updated_profile["is_default"],
            created_at=updated_profile["created_at"],
            updated_at=updated_profile["updated_at"],
            memory_count=memory_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating memory profile: {e}")
        # Check if it's a unique constraint violation
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A profile with the name '{update_data.name}' already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update memory profile"
        )


@router.delete("/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_memory_profile(
    profile_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a memory profile.
    
    Deletes a memory profile and all its associated memories. Cannot delete
    the profile if it's the user's only profile.
    
    Args:
        profile_id: Profile UUID
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if profile doesn't belong to user
        HTTPException: 404 if profile not found
        HTTPException: 400 if it's the only profile
        HTTPException: 500 if deletion fails
    """
    try:
        user_id = current_user["id"]
        
        # Get the profile to verify ownership
        profile = await supabase_service.get_memory_profile(profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory profile not found"
            )
        
        # Verify user has access to this profile
        verify_user_access(current_user, profile["user_id"])
        
        # Check if this is the only profile
        all_profiles = await supabase_service.get_memory_profiles(user_id)
        if len(all_profiles) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the only memory profile. Create another profile first."
            )
        
        # Delete all memories associated with this profile from mem0
        try:
            await mem0_service.delete_all_memories(user_id, profile_id)
        except Exception as e:
            print(f"Error deleting mem0 memories: {e}")
            # Continue with profile deletion even if memory deletion fails
        
        # Delete memory references from database
        try:
            # The database has CASCADE delete, so mem0_memories will be deleted automatically
            pass
        except Exception as e:
            print(f"Error deleting memory references: {e}")
        
        # Delete the profile (this will cascade delete mem0_memories and chat_sessions)
        success = await supabase_service.delete_memory_profile(profile_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete memory profile"
            )
        
        return {
            "message": "Memory profile deleted successfully",
            "profile_id": profile_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting memory profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete memory profile"
        )


@router.post("/{profile_id}/set-default", status_code=status.HTTP_200_OK)
async def set_default_memory_profile(
    profile_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Set a memory profile as the default.
    
    Sets the specified profile as the user's default profile and unsets
    any previously default profile.
    
    Args:
        profile_id: Profile UUID
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if profile doesn't belong to user
        HTTPException: 404 if profile not found
        HTTPException: 500 if update fails
    """
    try:
        # Get the profile to verify ownership
        profile = await supabase_service.get_memory_profile(profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory profile not found"
            )
        
        # Verify user has access to this profile
        verify_user_access(current_user, profile["user_id"])
        
        # Set as default (this will automatically unset other defaults)
        updated_profile = await supabase_service.set_default_memory_profile(profile_id)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set default memory profile"
            )
        
        return {
            "message": "Memory profile set as default successfully",
            "profile_id": profile_id,
            "profile_name": updated_profile["name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error setting default memory profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set default memory profile"
        )


@router.get("/{profile_id}/memories", response_model=List[MemoryResponse])
async def get_profile_memories(
    profile_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[MemoryResponse]:
    """
    Get all memories for a specific profile.
    
    Returns all memories stored in the specified memory profile.
    
    Args:
        profile_id: Profile UUID
        current_user: Current authenticated user (from dependency)
        
    Returns:
        List of MemoryResponse objects
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if profile doesn't belong to user
        HTTPException: 404 if profile not found
        HTTPException: 500 if retrieval fails
    """
    try:
        user_id = current_user["id"]
        
        # Get the profile to verify ownership
        profile = await supabase_service.get_memory_profile(profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory profile not found"
            )
        
        # Verify user has access to this profile
        verify_user_access(current_user, profile["user_id"])
        
        # Get memories from mem0
        memories = await mem0_service.get_memories(user_id, profile_id)
        
        # Convert to response models
        response_memories = []
        for mem in memories:
            # Handle different response formats from mem0
            memory_id = mem.get("id") or mem.get("memory_id") or ""
            memory_content = mem.get("memory") or mem.get("content") or mem.get("text") or ""
            created_at = mem.get("created_at")
            updated_at = mem.get("updated_at")
            metadata = mem.get("metadata")
            
            if memory_content:  # Only include memories with content
                response_memories.append(
                    MemoryResponse(
                        id=memory_id,
                        memory=memory_content,
                        created_at=created_at,
                        updated_at=updated_at,
                        user_id=user_id,
                        metadata=metadata
                    )
                )
        
        return response_memories
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memories"
        )
