"""
Example usage of role-based authorization dependencies in FastAPI routers.

This file demonstrates how to use the authorization dependencies
to protect routes based on user roles.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from app.models.user import User
from app.core.dependencies import (
    can_create_project,
    can_add_dataset_samples,
    can_view_analytics,
    can_submit_annotations,
    can_review_annotations
)

router = APIRouter()


# ============================================
# Admin-Only Operations
# ============================================

@router.post("/projects", status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: dict,  # Replace with actual ProjectCreate schema
    db: Session = Depends(get_db),
    current_user: User = Depends(can_create_project)
):
    """
    Create a new project.
    Only administrators can create projects.
    Returns 403 Forbidden if user is not admin.
    """
    # Only admins can reach here
    # Implementation would create project here
    return {"message": "Project created", "user": current_user.email}


@router.post("/projects/{project_id}/samples", status_code=status.HTTP_201_CREATED)
async def add_dataset_samples(
    project_id: uuid.UUID,
    samples: list[dict],  # Replace with actual DataSampleCreate schema
    db: Session = Depends(get_db),
    current_user: User = Depends(can_add_dataset_samples)
):
    """
    Add dataset samples to a project.
    Only administrators can add dataset samples.
    Returns 403 Forbidden if user is not admin.
    """
    # Only admins can reach here
    # Implementation would add samples here
    return {"message": f"Added {len(samples)} samples to project {project_id}"}


@router.get("/analytics")
async def view_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(can_view_analytics)
):
    """
    View system analytics and reports.
    Only administrators can view analytics.
    Returns 403 Forbidden if user is not admin.
    """
    # Only admins can reach here
    # Implementation would return analytics data here
    return {
        "total_projects": 0,
        "total_samples": 0,
        "total_annotations": 0,
        "total_reviews": 0
    }


# ============================================
# Annotator-Only Operations
# ============================================

@router.post("/samples/{sample_id}/annotations", status_code=status.HTTP_201_CREATED)
async def submit_annotation(
    sample_id: uuid.UUID,
    annotation: dict,  # Replace with actual AnnotationCreate schema
    db: Session = Depends(get_db),
    current_user: User = Depends(can_submit_annotations)
):
    """
    Submit an annotation for a data sample.
    Only annotators can submit annotations.
    Returns 403 Forbidden if user is not annotator.
    """
    # Only annotators can reach here
    # Implementation would create annotation here
    return {
        "message": "Annotation submitted",
        "sample_id": str(sample_id),
        "annotator": current_user.email
    }


# ============================================
# Reviewer-Only Operations
# ============================================

@router.post("/annotations/{annotation_id}/reviews", status_code=status.HTTP_201_CREATED)
async def review_annotation(
    annotation_id: uuid.UUID,
    review: dict,  # Replace with actual ReviewCreate schema
    db: Session = Depends(get_db),
    current_user: User = Depends(can_review_annotations)
):
    """
    Submit a review for an annotation.
    Only reviewers can review annotations.
    Returns 403 Forbidden if user is not reviewer.
    """
    # Only reviewers can reach here
    # Implementation would create review here
    return {
        "message": "Review submitted",
        "annotation_id": str(annotation_id),
        "reviewer": current_user.email
    }


# ============================================
# Example: Combining Multiple Dependencies
# ============================================

@router.get("/projects/{project_id}/summary")
async def get_project_summary(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_view_analytics)  # Admin only
):
    """
    Get detailed project summary with statistics.
    Only administrators can view project summaries.
    """
    # Only admins can reach here
    return {
        "project_id": str(project_id),
        "total_samples": 0,
        "annotated_samples": 0,
        "reviewed_samples": 0
    }
