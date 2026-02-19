from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.database import get_db
from app.models.user import User
from app.schemas.project import Project, ProjectCreate, ProjectWithStats
from app.services.project_service import ProjectService
from app.core.dependencies import get_current_user, can_create_project
from app.core.exceptions import handle_app_exception
from app.core.logging import logger

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "/",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    response_description="Project successfully created"
)
async def create_project(
    project_create: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_create_project)
):
    """
    Create a new project.
    
    **Admin only** - Only administrators can create projects.
    
    - **name**: Project name (required, 1-255 characters)
    - **description**: Optional project description
    
    Returns the created project object.
    """
    try:
        return ProjectService.create_project(db, project_create, current_user.id)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/",
    response_model=List[Project],
    summary="List all projects",
    response_description="List of projects"
)
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    created_by: Optional[uuid.UUID] = Query(None, description="Filter by creator ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of projects.
    
    Requires authentication. Optionally filter by creator.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-100)
    - **created_by**: Optional filter by creator user ID
    """
    try:
        return ProjectService.get_projects(db, skip=skip, limit=limit, created_by=created_by)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/{project_id}",
    response_model=Project,
    summary="Get project by ID",
    response_description="Project details"
)
async def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a project by ID.
    
    Requires authentication.
    """
    try:
        return ProjectService.get_project(db, project_id)
    except Exception as e:
        raise handle_app_exception(e)


@router.get(
    "/{project_id}/stats",
    response_model=ProjectWithStats,
    summary="Get project statistics",
    response_description="Project with statistics"
)
async def get_project_stats(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project statistics including sample counts by status.
    
    Requires authentication.
    """
    try:
        project = ProjectService.get_project(db, project_id)
        stats = ProjectService.get_project_stats(db, project_id)
        
        # Create response with stats
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_by": project.created_by,
            "created_at": project.created_at,
            **stats
        }
        return ProjectWithStats(**project_dict)
    except Exception as e:
        raise handle_app_exception(e)
