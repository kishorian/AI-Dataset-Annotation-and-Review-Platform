from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class Project(ProjectBase):
    """Schema for project response."""
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProjectWithStats(Project):
    """Project with statistics."""
    total_samples: int = 0
    pending_samples: int = 0
    annotated_samples: int = 0
    reviewed_samples: int = 0
