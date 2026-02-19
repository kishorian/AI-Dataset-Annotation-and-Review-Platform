from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    validate_password_strength
)
from app.core.exceptions import UnauthorizedError, ConflictError
from app.config import settings
from app.services.user_service import UserService
from app.core.logging import logger


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User | None:
        """
        Authenticate a user by email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Find user by email
        user = UserService.get_user_by_email(db, email)
        
        if not user:
            logger.warning(f"Authentication failed: user not found for email {email}")
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: incorrect password for user {user.id}")
            return None
        
        logger.info(f"User {user.id} authenticated successfully")
        return user
    
    @staticmethod
    def login(db: Session, email: str, password: str) -> Token:
        """
        Login a user and return an access token.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            Token object with access token
            
        Raises:
            UnauthorizedError: If authentication fails
        """
        user = AuthService.authenticate_user(db, email, password)
        if not user:
            raise UnauthorizedError("Incorrect email or password")
        
        # Create access token with user ID and role
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
            additional_claims={
                "email": user.email,
                "role": user.role.value
            }
        )
        
        logger.info(f"Access token created for user {user.id}")
        return Token(access_token=access_token, token_type="bearer")
    
    @staticmethod
    def register(db: Session, user_create: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_create: User creation data
            
        Returns:
            Created user object
            
        Raises:
            ConflictError: If user already exists
            ValueError: If password doesn't meet requirements
        """
        # Validate password strength
        is_valid, error_message = validate_password_strength(user_create.password)
        if not is_valid:
            raise ValueError(error_message or "Password does not meet requirements")
        
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_create.email)
        if existing_user:
            raise ConflictError(f"User with email {user_create.email} already exists")
        
        # Create user (password will be hashed in UserService)
        try:
            user = UserService.create_user(db, user_create)
            logger.info(f"New user registered: {user.id} ({user.email})")
            return user
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise
