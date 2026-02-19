from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid
from app.models.enums import ReviewDecision


class ReviewBase(BaseModel):
    decision: ReviewDecision = Field(..., description="Review decision")
    feedback: Optional[str] = Field(None, description="Review feedback")


class ReviewCreate(ReviewBase):
    """Schema for creating a new review."""
    annotation_id: uuid.UUID = Field(..., description="ID of the annotation being reviewed")


class Review(ReviewBase):
    """Schema for review response."""
    id: uuid.UUID
    annotation_id: uuid.UUID
    reviewer_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReviewWithDetails(Review):
    """Review with additional details."""
    reviewer_email: Optional[str] = None
    annotation_label: Optional[str] = None
    sample_id: Optional[uuid.UUID] = None
