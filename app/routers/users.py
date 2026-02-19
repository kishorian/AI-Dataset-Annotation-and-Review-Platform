from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.core.dependencies import get_current_active_user
from app.models.user import User as UserModel
from app.models.enums import UserRole
from app.core.exceptions import handle_app_exception

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get a list of users (requires authentication).
    """
    try:
        return UserService.get_users(db, skip=skip, limit=limit)
    except Exception as e:
        raise handle_app_exception(e)


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get a user by ID (requires authentication).
    """
    try:
        return UserService.get_user(db, user_id)
    except Exception as e:
        raise handle_app_exception(e)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update a user (requires authentication).
    Users can only update their own profile unless they are admins.
    """
    if user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        return UserService.update_user(db, user_id, user_update)
    except Exception as e:
        raise handle_app_exception(e)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Delete a user (requires authentication).
    Users can only delete their own account unless they are admins.
    """
    if user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        UserService.delete_user(db, user_id)
        return None
    except Exception as e:
        raise handle_app_exception(e)
