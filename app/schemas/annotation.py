from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid
from app.models.enums import AnnotationLabel


class AnnotationBase(BaseModel):
    label: AnnotationLabel = Field(..., description="Annotation label")


class AnnotationCreate(AnnotationBase):
    """Schema for creating a new annotation."""
    sample_id: uuid.UUID = Field(..., description="ID of the data sample being annotated")


class Annotation(AnnotationBase):
    """Schema for annotation response."""
    id: uuid.UUID
    sample_id: uuid.UUID
    annotator_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AnnotationWithDetails(Annotation):
    """Annotation with additional details."""
    annotator_email: Optional[str] = None
    sample_text: Optional[str] = None
    sample_status: Optional[str] = None
    review_count: int = 0
