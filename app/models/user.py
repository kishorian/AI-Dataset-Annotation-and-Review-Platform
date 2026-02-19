from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # Use Postgres enum values (e.g. "annotator") instead of names (e.g. "ANNOTATOR")
    role = Column(
        PGEnum(
            UserRole,
            name="userrole",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            create_type=False,  # enum type is managed by migrations
        ),
        nullable=False,
        default=UserRole.ANNOTATOR,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    created_projects = relationship("Project", back_populates="creator", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="annotator", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="reviewer", cascade="all, delete-orphan")
