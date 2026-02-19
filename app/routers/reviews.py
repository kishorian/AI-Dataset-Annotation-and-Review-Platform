from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.enums import ReviewDecision
from app.schemas.review import Review, ReviewCreate
from app.services.review_service import ReviewService
from app.core.dependencies import get_current_user, can_review_annotations
from app.core.exceptions import handle_app_exception

router = APIRouter(prefix="/reviews", tags=["reviews"])


class ApproveRequest(BaseModel):
    """Request schema for approving an annotation."""
    annotation_id: uuid.UUID
    feedback: Optional[str] = None


class RejectRequest(BaseModel):
    """Request schema for rejecting an annotation."""
    annotation_id: uuid.UUID
    feedback: str


@router.post(
    "/approve",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    summary="Approve an annotation",
    response_description="Annotation approved and sample status updated"
)
async def approve_annotation(
    request: ApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_review_annotations)
):
    """
    Approve an annotation.
    
    **Reviewer only** - Only reviewers can approve annotations.
    
    This operation:
    - Creates a review with 'approved' decision
    - Automatically updates the sample status to 'reviewed'
    - Both operations happen atomically in a single transaction
    
    The annotation's sample must be in 'annotated' status. If the sample
    is not in the correct status, the operation will fail with a 409 Conflict error.
    
    Request body:
    - **annotation_id**: ID of the annotation to approve
    - **feedback**: Optional feedback message
    
    Returns the created review object.
    """
    try:
        review_create = ReviewCreate(
            annotation_id=request.annotation_id,
            decision=ReviewDecision.APPROVED,
            feedback=request.feedback
        )
        return ReviewService.create_review(db, review_create, current_user.id)
    except Exception as e:
        raise handle_app_exception(e)


@router.post(
    "/reject",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    summary="Reject an annotation",
    response_description="Annotation rejected and sample status reset to pending"
)
async def reject_annotation(
    request: RejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_review_annotations)
):
    """
    Reject an annotation with feedback.
    
    **Reviewer only** - Only reviewers can reject annotations.
    
    This operation:
    - Creates a review with 'rejected' decision
    - Automatically updates the sample status back to 'pending'
    - Both operations happen atomically in a single transaction
    
    The annotation's sample must be in 'annotated' status. If the sample
    is not in the correct status, the operation will fail with a 409 Conflict error.
    
    Request body:
    - **annotation_id**: ID of the annotation to reject
    - **feedback**: Rejection feedback (required) - must explain why the annotation was rejected
    
    Returns the created review object.
    """
    try:
        review_create = ReviewCreate(
            annotation_id=request.annotation_id,
            decision=ReviewDecision.REJECTED,
            feedback=request.feedback
        )
        return ReviewService.create_review(db, review_create, current_user.id)
    except Exception as e:
        raise handle_app_exception(e)


@router.post(
    "/",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    summary="Create a review",
    response_description="Review created and sample status updated accordingly"
)
async def create_review(
    review_create: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_review_annotations)
):
    """
    Create a review for an annotation.
    
    **Reviewer only** - Only reviewers can create reviews.
    
    This operation:
    - Creates the review with the specified decision
    - If approved: updates sample status to 'reviewed'
    - If rejected: updates sample status back to 'pending'
    - Both operations happen atomically in a single transaction
    
    The annotation's sample must be in 'annotated' status.
    
    - **annotation_id**: ID of the annotation being reviewed
    - **decision**: Review decision (approved or rejected)
    - **feedback**: Optional feedback message (required for rejections)
    
    Returns the created review object.
    """
    try:
        # Validate feedback for rejections
        if review_create.decision == ReviewDecision.REJECTED and not review_create.feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback is required when rejecting an annotation"
            )
        
        return ReviewService.create_review(db, review_create, current_user.id)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/",
    response_model=List[Review],
    summary="Get reviews",
    response_description="List of reviews"
)
async def get_reviews(
    annotation_id: Optional[uuid.UUID] = Query(None, description="Filter by annotation ID"),
    reviewer_id: Optional[uuid.UUID] = Query(None, description="Filter by reviewer ID"),
    decision: Optional[ReviewDecision] = Query(None, description="Filter by decision"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of reviews with optional filtering.
    
    Requires authentication.
    
    - **annotation_id**: Optional filter by annotation ID
    - **reviewer_id**: Optional filter by reviewer ID
    - **decision**: Optional filter by decision (approved or rejected)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-100)
    """
    try:
        return ReviewService.get_reviews(
            db,
            annotation_id=annotation_id,
            reviewer_id=reviewer_id,
            decision=decision,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/{review_id}",
    response_model=Review,
    summary="Get review by ID",
    response_description="Review details"
)
async def get_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single review by ID.
    
    Requires authentication.
    """
    try:
        return ReviewService.get_review(db, review_id)
    except Exception as e:
        raise handle_app_exception(e)
