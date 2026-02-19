from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.database import get_db
from app.models.user import User
from app.models.enums import SampleStatus
from app.schemas.data_sample import DataSample, DataSampleCreate
from app.services.data_sample_service import DataSampleService
from app.core.dependencies import get_current_user, can_add_dataset_samples
from app.core.exceptions import handle_app_exception

router = APIRouter(prefix="/samples", tags=["data-samples"])


@router.post(
    "/",
    response_model=DataSample,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new data sample",
    response_description="Data sample successfully created"
)
async def add_sample(
    sample_create: DataSampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_add_dataset_samples)
):
    """
    Add a new data sample to a project.
    
    **Admin only** - Only administrators can add dataset samples.
    
    - **project_id**: ID of the project this sample belongs to
    - **text_content**: Text content of the data sample (required)
    
    The sample will be created with status 'pending'.
    Returns the created data sample object.
    """
    try:
        return DataSampleService.create_sample(db, sample_create)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/",
    response_model=List[DataSample],
    summary="Get data samples",
    response_description="List of data samples"
)
async def get_samples(
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    status: Optional[SampleStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of data samples with optional filtering.
    
    Requires authentication.
    
    - **project_id**: Optional filter by project ID
    - **status**: Optional filter by status (pending, annotated, reviewed)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-100)
    """
    try:
        return DataSampleService.get_samples(
            db,
            project_id=project_id,
            status=status,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/{sample_id}",
    response_model=DataSample,
    summary="Get data sample by ID",
    response_description="Data sample details"
)
async def get_sample(
    sample_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single data sample by ID.
    
    Requires authentication.
    """
    try:
        return DataSampleService.get_sample(db, sample_id)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/status/{status}",
    response_model=List[DataSample],
    summary="Get samples by status",
    response_description="List of data samples with specified status"
)
async def get_samples_by_status(
    status: SampleStatus,
    project_id: Optional[uuid.UUID] = Query(None, description="Optional filter by project ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get data samples filtered by status.
    
    Requires authentication.
    
    - **status**: Status to filter by (pending, annotated, reviewed)
    - **project_id**: Optional filter by project ID
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-100)
    """
    try:
        return DataSampleService.get_samples(
            db,
            project_id=project_id,
            status=status,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise handle_app_exception(e)
