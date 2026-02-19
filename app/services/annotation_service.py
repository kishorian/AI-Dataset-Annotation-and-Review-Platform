from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.models.annotation import Annotation
from app.models.data_sample import DataSample
from app.models.enums import SampleStatus
from app.schemas.annotation import AnnotationCreate
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import logger


class AnnotationService:
    @staticmethod
    def create_annotation(
        db: Session,
        annotation_create: AnnotationCreate,
        annotator_id: uuid.UUID
    ) -> Annotation:
        """
        Create a new annotation and update sample status to annotated.
        This operation is atomic - both annotation creation and status update
        happen in a single transaction.
        
        Args:
            db: Database session
            annotation_create: Annotation creation data
            annotator_id: ID of the annotator
            
        Returns:
            Created annotation
            
        Raises:
            NotFoundError: If sample not found
            ConflictError: If sample is not in pending status
        """
        try:
            # Get and verify sample exists
            sample = db.query(DataSample).filter(
                DataSample.id == annotation_create.sample_id
            ).first()
            
            if not sample:
                raise NotFoundError(f"Data sample with ID {annotation_create.sample_id} not found")
            
            # Verify sample is in pending status
            if sample.status != SampleStatus.PENDING:
                raise ConflictError(
                    f"Cannot annotate sample with status '{sample.status.value}'. "
                    f"Sample must be in 'pending' status."
                )
            
            # Create annotation
            db_annotation = Annotation(
                sample_id=annotation_create.sample_id,
                annotator_id=annotator_id,
                label=annotation_create.label
            )
            
            db.add(db_annotation)
            
            # Update sample status to annotated
            sample.status = SampleStatus.ANNOTATED
            
            # Commit both changes atomically
            db.commit()
            db.refresh(db_annotation)
            
            logger.info(
                f"Annotation created: {db_annotation.id} for sample {annotation_create.sample_id} "
                f"by annotator {annotator_id}. Sample status updated to annotated."
            )
            
            return db_annotation
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating annotation: {e}")
            raise ConflictError("Failed to create annotation due to database constraint")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating annotation: {e}")
            raise
    
    @staticmethod
    def get_annotation(db: Session, annotation_id: uuid.UUID) -> Annotation:
        """
        Get an annotation by ID.
        
        Args:
            db: Database session
            annotation_id: Annotation ID
            
        Returns:
            Annotation object
            
        Raises:
            NotFoundError: If annotation not found
        """
        annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
        if not annotation:
            raise NotFoundError(f"Annotation with ID {annotation_id} not found")
        return annotation
    
    @staticmethod
    def get_annotations(
        db: Session,
        sample_id: Optional[uuid.UUID] = None,
        annotator_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Annotation]:
        """
        Get list of annotations with optional filtering.
        
        Args:
            db: Database session
            sample_id: Optional filter by sample ID
            annotator_id: Optional filter by annotator ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of annotations
        """
        query = db.query(Annotation)
        
        if sample_id:
            query = query.filter(Annotation.sample_id == sample_id)
        
        if annotator_id:
            query = query.filter(Annotation.annotator_id == annotator_id)
        
        return query.order_by(Annotation.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_annotation(db: Session, annotation_id: uuid.UUID) -> None:
        """
        Delete an annotation.
        
        Args:
            db: Database session
            annotation_id: Annotation ID
            
        Raises:
            NotFoundError: If annotation not found
        """
        annotation = AnnotationService.get_annotation(db, annotation_id)
        db.delete(annotation)
        db.commit()
        logger.info(f"Annotation deleted: {annotation_id}")
