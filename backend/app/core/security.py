"""
Security module.
Handles authentication, authorization, and security configurations.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from supabase import create_client, Client
from app.core.config import settings
from app.services.supabase_service import supabase_service


# HTTP Bearer token scheme
security_scheme = HTTPBearer()


class SecurityService:
    """
    Service class for security operations.
    Handles JWT verification, user authentication, and authorization.
    """
    
    def __init__(self):
        """Initialize security service with Supabase client."""
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY  # Use anon key for client operations
        )
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
    
    # ========================
    # JWT Verification
    # ========================
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and extract payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            print(f"JWT verification error: {e}")
            return None
    
    def verify_supabase_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Supabase JWT token.
        
        Supabase tokens are signed with the JWT secret from Supabase settings.
        This method verifies the token using Supabase's verification.
        
        Args:
            token: JWT token from Supabase auth
            
        Returns:
            User data if valid, None otherwise
        """
        try:
            # Get user from Supabase using the token
            response = self.supabase.auth.get_user(token)
            if response and response.user:
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "user": response.user
                }
            return None
        except Exception as e:
            print(f"Supabase token verification error: {e}")
            return None
    
    # ========================
    # User Authentication
    # ========================
    
    async def get_current_user_from_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current user from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            User data if authenticated, None otherwise
        """
        # Verify token with Supabase
        token_data = self.verify_supabase_token(token)
        if not token_data:
            return None
        
        user_id = token_data.get("user_id")
        if not user_id:
            return None
        
        # Get user from database
        user = await supabase_service.get_user_by_id(user_id)
        if not user:
            # User exists in auth but not in database - create user record
            email = token_data.get("email")
            if email:
                user = await supabase_service.create_user(email, user_id)
        
        return user
    
    def validate_user_access(
        self,
        user_id: str,
        resource_user_id: str
    ) -> bool:
        """
        Validate that a user has access to a resource.
        
        Args:
            user_id: Current user's ID
            resource_user_id: User ID that owns the resource
            
        Returns:
            True if user has access, False otherwise
        """
        return user_id == resource_user_id
    
    # ========================
    # Password Hashing (for custom auth if needed)
    # ========================
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)


# Create singleton instance
security_service = SecurityService()


# ========================
# FastAPI Dependencies
# ========================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Extracts JWT token from Authorization header, verifies it,
    and returns the user object.
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        User object from database
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Extract token
    token = credentials.credentials
    
    # Verify token and get user
    user = await security_service.get_current_user_from_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to get current user (optional).
    
    Similar to get_current_user but doesn't raise error if no token provided.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    user = await security_service.get_current_user_from_token(token)
    
    return user


def verify_user_access(
    current_user: Dict[str, Any],
    resource_user_id: str
) -> None:
    """
    Verify that current user has access to a resource.
    
    Args:
        current_user: Current authenticated user
        resource_user_id: User ID that owns the resource
        
    Raises:
        HTTPException: 403 if user doesn't have access
    """
    if not security_service.validate_user_access(
        current_user["id"],
        resource_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )


# ========================
# CORS Configuration
# ========================

def get_cors_config() -> Dict[str, Any]:
    """
    Get CORS configuration for FastAPI.
    
    Returns:
        Dictionary with CORS settings
    """
    return {
        "allow_origins": settings.CORS_ORIGINS,
        "allow_credentials": settings.CORS_CREDENTIALS,
        "allow_methods": settings.CORS_METHODS,
        "allow_headers": settings.CORS_HEADERS,
    }


# ========================
# Rate Limiting Configuration
# ========================

class RateLimitConfig:
    """Configuration for rate limiting."""
    
    def __init__(self):
        """Initialize rate limit configuration from settings."""
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.per_minute = settings.RATE_LIMIT_PER_MINUTE
    
    def is_enabled(self) -> bool:
        """Check if rate limiting is enabled."""
        return self.enabled
    
    def get_limit(self) -> int:
        """Get rate limit per minute."""
        return self.per_minute
    
    def get_limit_string(self) -> str:
        """Get rate limit as string for headers."""
        return f"{self.per_minute}/minute"


# Create rate limit config instance
rate_limit_config = RateLimitConfig()


# ========================
# Security Headers
# ========================

def get_security_headers() -> Dict[str, str]:
    """
    Get security headers to add to responses.
    
    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }


# ========================
# API Key Validation (for service-to-service calls)
# ========================

class APIKeyAuth:
    """API Key authentication for service-to-service calls."""
    
    def __init__(self, api_key_header: str = "X-API-Key"):
        """
        Initialize API key authentication.
        
        Args:
            api_key_header: Header name for API key
        """
        self.api_key_header = api_key_header
        self.valid_keys = []  # In production, load from secure storage
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        return api_key in self.valid_keys
    
    def add_api_key(self, api_key: str) -> None:
        """
        Add a valid API key.
        
        Args:
            api_key: API key to add
        """
        if api_key not in self.valid_keys:
            self.valid_keys.append(api_key)
    
    def remove_api_key(self, api_key: str) -> None:
        """
        Remove an API key.
        
        Args:
            api_key: API key to remove
        """
        if api_key in self.valid_keys:
            self.valid_keys.remove(api_key)


# Create API key auth instance
api_key_auth = APIKeyAuth()
