from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid


class Token(BaseModel):
    """JWT access token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class TokenVerifyRequest(BaseModel):
    """Token verification request schema."""
    token: str = Field(..., description="JWT access token to verify")


class TokenVerifyResponse(BaseModel):
    """Token verification response."""
    valid: bool = Field(..., description="Whether the token is valid")
    message: str = Field(..., description="Verification message")