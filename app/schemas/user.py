from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
import uuid
from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.ANNOTATOR


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    hashed_password: str
