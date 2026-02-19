from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.database import get_db
from app.schemas.auth import Token
from app.schemas.user import UserCreate, User as UserSchema
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_active_user
from app.core.security import verify_token
from app.models.user import User as UserModel
from app.core.exceptions import handle_app_exception, UnauthorizedError, ConflictError
from app.core.logging import logger
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="User successfully registered"
)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (must be at least 8 characters, contain uppercase, lowercase, and digit)
    - **role**: User's role (default: annotator)
    
    Returns the created user object (password is excluded).
    """
    try:
        return AuthService.register(db, user_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        # Include error details in development, generic message in production
        error_detail = str(e) if settings.DEBUG else "An error occurred during registration"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
    response_description="Access token for authenticated requests"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and receive an access token.
    
    - **username**: User's email address (OAuth2 uses 'username' field)
    - **password**: User's password
    
    Returns a JWT access token that should be included in subsequent requests
    as a Bearer token in the Authorization header.
    
    Token format: `Authorization: Bearer <access_token>`
    """
    try:
        # OAuth2PasswordRequestForm uses 'username' field for email
        return AuthService.login(db, form_data.username, form_data.password)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.post(
    "/verify-token",
    status_code=status.HTTP_200_OK,
    summary="Verify access token",
    response_description="Token validity status"
)
async def verify_access_token(
    token: str = Body(..., embed=True, description="JWT access token to verify")
):
    """
    Verify if an access token is valid.
    
    - **token**: JWT access token to verify
    
    Returns whether the token is valid or not.
    """
    is_valid = verify_token(token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return {"valid": True, "message": "Token is valid"}


@router.get(
    "/me",
    response_model=UserSchema,
    summary="Get current user information",
    response_description="Current authenticated user details"
)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get information about the currently authenticated user.
    
    Requires a valid JWT access token in the Authorization header.
    
    Returns the user's information including ID, email, role, and creation date.
    """
    return current_user
