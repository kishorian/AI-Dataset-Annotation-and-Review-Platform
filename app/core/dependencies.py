from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import decode_access_token, verify_token
from app.core.logging import logger

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scheme_name="JWT",
    auto_error=False  # We'll handle errors manually
)

# HTTP Bearer scheme as alternative
http_bearer = HTTPBearer(auto_error=False)


async def get_token_from_request(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    token: Optional[str] = Depends(oauth2_scheme)
) -> str:
    """
    Extract token from request (supports both OAuth2 and Bearer schemes).
    
    Args:
        credentials: HTTP Bearer credentials
        token: OAuth2 token
        
    Returns:
        Token string
        
    Raises:
        HTTPException: If no token is provided
    """
    if credentials:
        return credentials.credentials
    elif token:
        return token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode and verify token
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Invalid or expired token")
        raise credentials_exception
    
    # Extract user ID from token
    user_id_str = payload.get("sub")
    if user_id_str is None:
        logger.warning("Token missing 'sub' claim")
        raise credentials_exception
    
    # Convert to UUID
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid user ID format in token: {e}")
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user.
    This is a wrapper around get_current_user for consistency.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current authenticated user
    """
    return current_user


def require_roles(allowed_roles: List[UserRole]):
    """
    Create a dependency that requires specific roles.
    
    Args:
        allowed_roles: List of roles that are allowed to access
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Check if current user has required role.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Current user if authorized
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in allowed_roles:
            logger.warning(
                f"User {current_user.id} with role {current_user.role} "
                f"attempted to access resource requiring {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    
    return role_checker


# Pre-defined role-based dependencies
async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user {current_user.id} attempted admin operation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin role"
        )
    return current_user


async def require_reviewer(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires reviewer or admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if reviewer or admin
        
    Raises:
        HTTPException: If user is not reviewer or admin
    """
    if current_user.role not in [UserRole.REVIEWER, UserRole.ADMIN]:
        logger.warning(f"User {current_user.id} with role {current_user.role} attempted reviewer operation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires reviewer or admin role"
        )
    return current_user


async def require_annotator(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires annotator, reviewer, or admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if annotator, reviewer, or admin
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    if current_user.role not in [UserRole.ANNOTATOR, UserRole.REVIEWER, UserRole.ADMIN]:
        logger.warning(f"User {current_user.id} with role {current_user.role} attempted annotator operation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires annotator, reviewer, or admin role"
        )
    return current_user


# Operation-specific authorization dependencies

async def can_create_project(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that allows only admin to create projects.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"User {current_user.id} with role {current_user.role.value} "
            f"attempted to create a project (admin only)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create projects"
        )
    return current_user


async def can_add_dataset_samples(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that allows only admin to add dataset samples.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"User {current_user.id} with role {current_user.role.value} "
            f"attempted to add dataset samples (admin only)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can add dataset samples"
        )
    return current_user


async def can_view_analytics(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that allows only admin to view analytics.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"User {current_user.id} with role {current_user.role.value} "
            f"attempted to view analytics (admin only)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view analytics"
        )
    return current_user


async def can_submit_annotations(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that allows only annotators to submit annotations.
    
    Note: Admins and reviewers can also submit annotations as they have
    broader permissions, but this dependency is specifically for annotator-only operations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if annotator
        
    Raises:
        HTTPException: 403 if user is not annotator
    """
    if current_user.role != UserRole.ANNOTATOR:
        logger.warning(
            f"User {current_user.id} with role {current_user.role.value} "
            f"attempted to submit annotation (annotator only)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only annotators can submit annotations"
        )
    return current_user


async def can_review_annotations(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that allows only reviewers to review annotations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if reviewer
        
    Raises:
        HTTPException: 403 if user is not reviewer
    """
    if current_user.role != UserRole.REVIEWER:
        logger.warning(
            f"User {current_user.id} with role {current_user.role.value} "
            f"attempted to review annotation (reviewer only)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only reviewers can review annotations"
        )
    return current_user
