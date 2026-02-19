from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.models.data_sample import DataSample
from app.models.project import Project
from app.models.enums import SampleStatus
from app.schemas.data_sample import DataSampleCreate, DataSampleUpdate
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import logger


class DataSampleService:
    @staticmethod
    def create_sample(db: Session, sample_create: DataSampleCreate) -> DataSample:
        """
        Create a new data sample with transactional consistency.
        
        Args:
            db: Database session
            sample_create: Sample creation data
            
        Returns:
            Created data sample
            
        Raises:
            NotFoundError: If project not found
        """
        try:
            # Verify project exists
            project = db.query(Project).filter(Project.id == sample_create.project_id).first()
            if not project:
                raise NotFoundError(f"Project with ID {sample_create.project_id} not found")
            
            db_sample = DataSample(
                project_id=sample_create.project_id,
                text_content=sample_create.text_content,
                status=SampleStatus.PENDING
            )
            
            db.add(db_sample)
            db.commit()
            db.refresh(db_sample)
            
            logger.info(f"Data sample created: {db_sample.id} for project {sample_create.project_id}")
            return db_sample
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating data sample: {e}")
            raise ConflictError("Failed to create data sample due to database constraint")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating data sample: {e}")
            raise
    
    @staticmethod
    def get_sample(db: Session, sample_id: uuid.UUID) -> DataSample:
        """
        Get a data sample by ID.
        
        Args:
            db: Database session
            sample_id: Sample ID
            
        Returns:
            Data sample object
            
        Raises:
            NotFoundError: If sample not found
        """
        sample = db.query(DataSample).filter(DataSample.id == sample_id).first()
        if not sample:
            raise NotFoundError(f"Data sample with ID {sample_id} not found")
        return sample
    
    @staticmethod
    def get_samples(
        db: Session,
        project_id: Optional[uuid.UUID] = None,
        status: Optional[SampleStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DataSample]:
        """
        Get list of data samples with optional filtering.
        
        Args:
            db: Database session
            project_id: Optional filter by project ID
            status: Optional filter by status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of data samples
        """
        query = db.query(DataSample)
        
        if project_id:
            query = query.filter(DataSample.project_id == project_id)
        
        if status:
            query = query.filter(DataSample.status == status)
        
        return query.order_by(DataSample.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_sample_status(
        db: Session,
        sample_id: uuid.UUID,
        new_status: SampleStatus
    ) -> DataSample:
        """
        Update sample status with transactional consistency.
        
        Args:
            db: Database session
            sample_id: Sample ID
            new_status: New status to set
            
        Returns:
            Updated data sample
            
        Raises:
            NotFoundError: If sample not found
        """
        sample = DataSampleService.get_sample(db, sample_id)
        sample.status = new_status
        
        try:
            db.commit()
            db.refresh(sample)
            logger.info(f"Sample {sample_id} status updated to {new_status.value}")
            return sample
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating sample status: {e}")
            raise
    
    @staticmethod
    def update_sample(db: Session, sample_id: uuid.UUID, sample_update: DataSampleUpdate) -> DataSample:
        """
        Update a data sample.
        
        Args:
            db: Database session
            sample_id: Sample ID
            sample_update: Update data
            
        Returns:
            Updated data sample
            
        Raises:
            NotFoundError: If sample not found
        """
        sample = DataSampleService.get_sample(db, sample_id)
        
        update_data = sample_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(sample, field, value)
        
        try:
            db.commit()
            db.refresh(sample)
            logger.info(f"Data sample updated: {sample_id}")
            return sample
        except IntegrityError:
            db.rollback()
            raise ConflictError("Failed to update data sample due to database constraint")
    
    @staticmethod
    def delete_sample(db: Session, sample_id: uuid.UUID) -> None:
        """
        Delete a data sample.
        
        Args:
            db: Database session
            sample_id: Sample ID
            
        Raises:
            NotFoundError: If sample not found
        """
        sample = DataSampleService.get_sample(db, sample_id)
        db.delete(sample)
        db.commit()
        logger.info(f"Data sample deleted: {sample_id}")
