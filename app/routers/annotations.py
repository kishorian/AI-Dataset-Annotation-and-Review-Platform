from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.database import get_db
from app.models.user import User
from app.schemas.annotation import Annotation, AnnotationCreate
from app.services.annotation_service import AnnotationService
from app.core.dependencies import get_current_user, can_submit_annotations
from app.core.exceptions import handle_app_exception

router = APIRouter(prefix="/annotations", tags=["annotations"])


@router.post(
    "/",
    response_model=Annotation,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an annotation",
    response_description="Annotation successfully submitted"
)
async def submit_annotation(
    annotation_create: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_submit_annotations)
):
    """
    Submit an annotation for a data sample.
    
    **Annotator only** - Only annotators can submit annotations.
    
    This operation:
    - Creates the annotation
    - Automatically updates the sample status from 'pending' to 'annotated'
    - Both operations happen atomically in a single transaction
    
    - **sample_id**: ID of the data sample being annotated
    - **label**: Annotation label (positive, negative, or neutral)
    
    The sample must be in 'pending' status. If the sample is already annotated
    or reviewed, the operation will fail with a 409 Conflict error.
    
    Returns the created annotation object.
    """
    try:
        return AnnotationService.create_annotation(db, annotation_create, current_user.id)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/",
    response_model=List[Annotation],
    summary="Get annotations",
    response_description="List of annotations"
)
async def get_annotations(
    sample_id: Optional[uuid.UUID] = Query(None, description="Filter by sample ID"),
    annotator_id: Optional[uuid.UUID] = Query(None, description="Filter by annotator ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of annotations with optional filtering.
    
    Requires authentication.
    
    - **sample_id**: Optional filter by sample ID
    - **annotator_id**: Optional filter by annotator ID
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-100)
    """
    try:
        return AnnotationService.get_annotations(
            db,
            sample_id=sample_id,
            annotator_id=annotator_id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/{annotation_id}",
    response_model=Annotation,
    summary="Get annotation by ID",
    response_description="Annotation details"
)
async def get_annotation(
    annotation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single annotation by ID.
    
    Requires authentication.
    """
    try:
        return AnnotationService.get_annotation(db, annotation_id)
    except Exception as e:
        raise handle_app_exception(e)
