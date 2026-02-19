from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundError, ConflictError


class UserService:
    @staticmethod
    def get_user(db: Session, user_id: uuid.UUID) -> User:
        """
        Get a user by ID.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """
        Get a user by email.
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get a list of users with pagination.
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        Create a new user.
        """
        # Check if user already exists
        if UserService.get_user_by_email(db, user_create.email):
            raise ConflictError(f"User with email {user_create.email} already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            role=user_create.role if hasattr(user_create, "role") else None,
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            db.rollback()
            raise ConflictError("User creation failed due to integrity constraint")
        except Exception as e:
            db.rollback()
            # Re-raise with more context
            raise Exception(f"Database error creating user: {str(e)}") from e
    
    @staticmethod
    def update_user(db: Session, user_id: uuid.UUID, user_update: UserUpdate) -> User:
        """
        Update a user.
        """
        user = UserService.get_user(db, user_id)
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # Check for conflicts
        if "email" in update_data:
            existing_user = UserService.get_user_by_email(db, update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ConflictError(f"User with email {update_data['email']} already exists")
        
        # Update user
        for field, value in update_data.items():
            setattr(user, field, value)
        
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ConflictError("User update failed due to integrity constraint")
    
    @staticmethod
    def delete_user(db: Session, user_id: uuid.UUID) -> None:
        """
        Delete a user.
        """
        user = UserService.get_user(db, user_id)
        db.delete(user)
        db.commit()
