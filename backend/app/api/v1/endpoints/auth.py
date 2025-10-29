"""
Authentication endpoints.
Handles user signup, login, logout, and user info.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from supabase import create_client, Client
from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.supabase_service import supabase_service


# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_supabase_client() -> Client:
    """Get Supabase client for auth operations."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate) -> TokenResponse:
    """
    Sign up a new user.
    
    Creates a new user in Supabase Auth, creates a user record in the database,
    and creates a default memory profile for the user.
    
    Args:
        user_data: User registration data (email, password)
        
    Returns:
        TokenResponse with access token and user information
        
    Raises:
        HTTPException: 400 if user already exists or validation fails
        HTTPException: 500 if user creation fails
    """
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed. Email may already be in use."
            )
        
        user_id = auth_response.user.id
        
        # Create user record in database
        try:
            db_user = await supabase_service.create_user(
                email=user_data.email,
                user_id=user_id
            )
        except Exception as e:
            # If database user creation fails, we should ideally clean up the auth user
            # For now, we'll let it proceed as the user is created in auth
            print(f"Database user creation error: {e}")
            # Try to get the user if it already exists
            db_user = await supabase_service.get_user_by_id(user_id)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user record in database"
                )
        
        # Create default memory profile
        try:
            await supabase_service.create_memory_profile(
                user_id=user_id,
                name="Default",
                description="Your default memory profile",
                is_default=True
            )
        except Exception as e:
            print(f"Error creating default memory profile: {e}")
            # Continue even if profile creation fails - user can create one later
        
        # Prepare response
        user_response = UserResponse(
            id=db_user["id"],
            email=db_user["email"],
            created_at=db_user["created_at"],
            updated_at=db_user["updated_at"],
            metadata=db_user.get("metadata")
        )
        
        # Get token information
        access_token = auth_response.session.access_token if auth_response.session else ""
        expires_in = auth_response.session.expires_in if auth_response.session else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin) -> TokenResponse:
    """
    Log in an existing user.
    
    Authenticates user with Supabase Auth and returns access token.
    
    Args:
        credentials: User login credentials (email, password)
        
    Returns:
        TokenResponse with access token and user information
        
    Raises:
        HTTPException: 401 if credentials are invalid
        HTTPException: 500 if authentication fails
    """
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_id = auth_response.user.id
        
        # Get user from database
        db_user = await supabase_service.get_user_by_id(user_id)
        
        if not db_user:
            # User exists in auth but not in database - create user record
            db_user = await supabase_service.create_user(
                email=auth_response.user.email,
                user_id=user_id
            )
        
        # Prepare response
        user_response = UserResponse(
            id=db_user["id"],
            email=db_user["email"],
            created_at=db_user["created_at"],
            updated_at=db_user["updated_at"],
            metadata=db_user.get("metadata")
        )
        
        return TokenResponse(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            expires_in=auth_response.session.expires_in,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Log out the current user.
    
    Invalidates the user's session token in Supabase.
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 500 if logout fails
    """
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Sign out from Supabase (invalidates the session)
        supabase.auth.sign_out()
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        print(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Returns the profile information of the currently authenticated user.
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        UserResponse with user information
        
    Raises:
        HTTPException: 401 if not authenticated
    """
    try:
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            created_at=current_user["created_at"],
            updated_at=current_user["updated_at"],
            metadata=current_user.get("metadata")
        )
    except KeyError as e:
        print(f"Missing user field: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User data is incomplete"
        )
