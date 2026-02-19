from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from app.core.logging import logger

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password using bcrypt.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password string
    """
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # bcrypt only considers the first 72 bytes of the password.
    # Enforce this explicitly to avoid confusing behavior and passlib errors.
    if len(password.encode("utf-8")) > 72:
        return (
            False,
            "Password cannot be longer than 72 bytes (bcrypt limit). "
            "Use a shorter password (especially if using emojis/non-ASCII).",
        )

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Secondary (UX) upper bound (bcrypt is already enforced above).
    if len(password) > 128:
        return False, "Password must be 128 characters or fewer"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, None


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create a JWT access token with expiration.
    
    Args:
        data: Dictionary containing token payload (must include 'sub' for user ID)
        expires_delta: Optional custom expiration time
        additional_claims: Optional additional claims to include in token
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Add additional claims if provided
    if additional_claims:
        to_encode.update(additional_claims)
    
    # Convert UUID to string if present
    if "sub" in to_encode:
        if hasattr(to_encode["sub"], "__str__"):
            to_encode["sub"] = str(to_encode["sub"])
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at time
        "type": "access"  # Token type
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: The JWT token string to decode
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != "access":
            logger.warning("Token type mismatch")
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        return None


def verify_token(token: str) -> bool:
    """
    Verify if a token is valid.
    
    Args:
        token: The JWT token string to verify
        
    Returns:
        True if token is valid, False otherwise
    """
    payload = decode_access_token(token)
    return payload is not None
