from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.database import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import AnalyticsService
from app.core.dependencies import get_current_user, can_view_analytics
from app.core.exceptions import handle_app_exception

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/",
    response_model=AnalyticsResponse,
    summary="Get system-wide analytics",
    response_description="Comprehensive analytics for the entire system"
)
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(can_view_analytics)
):
    """
    Get comprehensive system-wide analytics.
    
    **Admin only** - Only administrators can view analytics.
    
    Returns:
    - **total_samples**: Total number of data samples in the system
    - **pending_samples**: Number of samples with 'pending' status
    - **annotated_samples**: Number of samples with 'annotated' status
    - **reviewed_samples**: Number of samples with 'reviewed' status
    - **approval_rate**: Percentage of reviews that were approved (0-100)
    - **rejection_rate**: Percentage of reviews that were rejected (0-100)
    - **annotator_contribution_count**: Number of unique annotators who have submitted annotations
    
    All queries use efficient aggregate functions to minimize database load.
    """
    try:
        return AnalyticsService.get_analytics(db)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/project/{project_id}",
    response_model=AnalyticsResponse,
    summary="Get project-specific analytics",
    response_description="Analytics for a specific project"
)
async def get_project_analytics(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_view_analytics)
):
    """
    Get analytics for a specific project.
    
    **Admin only** - Only administrators can view analytics.
    
    Returns the same metrics as system-wide analytics, but filtered to the specified project.
    
    - **project_id**: UUID of the project to get analytics for
    """
    try:
        analytics_dict = AnalyticsService.get_project_analytics(db, str(project_id))
        return AnalyticsResponse(**analytics_dict)
    except Exception as e:
        raise handle_app_exception(e)
