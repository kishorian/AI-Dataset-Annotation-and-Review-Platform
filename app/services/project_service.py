from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.models.project import Project
from app.models.data_sample import DataSample
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import logger


class ProjectService:
    @staticmethod
    def create_project(db: Session, project_create: ProjectCreate, created_by: uuid.UUID) -> Project:
        """
        Create a new project with transactional consistency.
        
        Args:
            db: Database session
            project_create: Project creation data
            created_by: ID of the user creating the project
            
        Returns:
            Created project
            
        Raises:
            ConflictError: If project name already exists
        """
        try:
            # Check if project with same name exists
            existing = db.query(Project).filter(Project.name == project_create.name).first()
            if existing:
                raise ConflictError(f"Project with name '{project_create.name}' already exists")
            
            db_project = Project(
                name=project_create.name,
                description=project_create.description,
                created_by=created_by
            )
            
            db.add(db_project)
            db.commit()
            db.refresh(db_project)
            
            logger.info(f"Project created: {db_project.id} by user {created_by}")
            return db_project
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating project: {e}")
            raise ConflictError("Failed to create project due to database constraint")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating project: {e}")
            raise
    
    @staticmethod
    def get_project(db: Session, project_id: uuid.UUID) -> Project:
        """
        Get a project by ID.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Project object
            
        Raises:
            NotFoundError: If project not found
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError(f"Project with ID {project_id} not found")
        return project
    
    @staticmethod
    def get_projects(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        created_by: Optional[uuid.UUID] = None
    ) -> List[Project]:
        """
        Get list of projects with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            created_by: Optional filter by creator ID
            
        Returns:
            List of projects
        """
        query = db.query(Project)
        
        if created_by:
            query = query.filter(Project.created_by == created_by)
        
        return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_project(db: Session, project_id: uuid.UUID, project_update: ProjectUpdate) -> Project:
        """
        Update a project.
        
        Args:
            db: Database session
            project_id: Project ID
            project_update: Update data
            
        Returns:
            Updated project
            
        Raises:
            NotFoundError: If project not found
            ConflictError: If new name conflicts with existing project
        """
        project = ProjectService.get_project(db, project_id)
        
        update_data = project_update.model_dump(exclude_unset=True)
        
        # Check for name conflict
        if "name" in update_data:
            existing = db.query(Project).filter(
                Project.name == update_data["name"],
                Project.id != project_id
            ).first()
            if existing:
                raise ConflictError(f"Project with name '{update_data['name']}' already exists")
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        try:
            db.commit()
            db.refresh(project)
            logger.info(f"Project updated: {project_id}")
            return project
        except IntegrityError:
            db.rollback()
            raise ConflictError("Failed to update project due to database constraint")
    
    @staticmethod
    def delete_project(db: Session, project_id: uuid.UUID) -> None:
        """
        Delete a project (cascades to data samples).
        
        Args:
            db: Database session
            project_id: Project ID
            
        Raises:
            NotFoundError: If project not found
        """
        project = ProjectService.get_project(db, project_id)
        db.delete(project)
        db.commit()
        logger.info(f"Project deleted: {project_id}")
    
    @staticmethod
    def get_project_stats(db: Session, project_id: uuid.UUID) -> dict:
        """
        Get statistics for a project.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Dictionary with project statistics
        """
        project = ProjectService.get_project(db, project_id)
        
        total = db.query(DataSample).filter(DataSample.project_id == project_id).count()
        pending = db.query(DataSample).filter(
            DataSample.project_id == project_id,
            DataSample.status == "pending"
        ).count()
        annotated = db.query(DataSample).filter(
            DataSample.project_id == project_id,
            DataSample.status == "annotated"
        ).count()
        reviewed = db.query(DataSample).filter(
            DataSample.project_id == project_id,
            DataSample.status == "reviewed"
        ).count()
        
        return {
            "total_samples": total,
            "pending_samples": pending,
            "annotated_samples": annotated,
            "reviewed_samples": reviewed
        }
