from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid
from app.models.enums import SampleStatus


class DataSampleBase(BaseModel):
    text_content: str = Field(..., min_length=1, description="Text content of the data sample")


class DataSampleCreate(DataSampleBase):
    """Schema for creating a new data sample."""
    project_id: uuid.UUID = Field(..., description="ID of the project this sample belongs to")


class DataSampleUpdate(BaseModel):
    """Schema for updating a data sample."""
    text_content: Optional[str] = Field(None, min_length=1)
    status: Optional[SampleStatus] = None


class DataSample(DataSampleBase):
    """Schema for data sample response."""
    id: uuid.UUID
    project_id: uuid.UUID
    status: SampleStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DataSampleWithProject(DataSample):
    """Data sample with project information."""
    project_name: Optional[str] = None
