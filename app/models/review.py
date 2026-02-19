from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app.models.enums import ReviewDecision


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    annotation_id = Column(UUID(as_uuid=True), ForeignKey("annotations.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    decision = Column(Enum(ReviewDecision), nullable=False, index=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    annotation = relationship("Annotation", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
    
    # Indexes
    __table_args__ = (
        Index("idx_review_annotation_id", "annotation_id"),
        Index("idx_review_reviewer_id", "reviewer_id"),
        Index("idx_review_decision", "decision"),
        Index("idx_review_annotation_reviewer", "annotation_id", "reviewer_id"),
    )
