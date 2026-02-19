from pydantic import BaseModel, Field


class AnalyticsResponse(BaseModel):
    """Analytics response schema."""
    total_samples: int = Field(..., description="Total number of data samples")
    pending_samples: int = Field(..., description="Number of samples with pending status")
    annotated_samples: int = Field(..., description="Number of samples with annotated status")
    reviewed_samples: int = Field(..., description="Number of samples with reviewed status")
    approval_rate: float = Field(..., ge=0, le=100, description="Approval rate percentage")
    rejection_rate: float = Field(..., ge=0, le=100, description="Rejection rate percentage")
    annotator_contribution_count: int = Field(..., description="Number of unique annotators who have submitted annotations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_samples": 1000,
                "pending_samples": 200,
                "annotated_samples": 500,
                "reviewed_samples": 300,
                "approval_rate": 75.5,
                "rejection_rate": 24.5,
                "annotator_contribution_count": 25
            }
        }
