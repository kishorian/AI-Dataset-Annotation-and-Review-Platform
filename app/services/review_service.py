from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.models.review import Review
from app.models.annotation import Annotation
from app.models.data_sample import DataSample
from app.models.enums import ReviewDecision, SampleStatus
from app.schemas.review import ReviewCreate
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import logger


class ReviewService:
    @staticmethod
    def create_review(
        db: Session,
        review_create: ReviewCreate,
        reviewer_id: uuid.UUID
    ) -> Review:
        """
        Create a review and update sample status based on decision.
        This operation is atomic - review creation and status update
        happen in a single transaction.
        
        - If approved: sample status becomes 'reviewed'
        - If rejected: sample status returns to 'pending'
        
        Args:
            db: Database session
            review_create: Review creation data
            reviewer_id: ID of the reviewer
            
        Returns:
            Created review
            
        Raises:
            NotFoundError: If annotation not found
            ConflictError: If annotation is already reviewed
        """
        try:
            # Get and verify annotation exists
            annotation = db.query(Annotation).filter(
                Annotation.id == review_create.annotation_id
            ).first()
            
            if not annotation:
                raise NotFoundError(f"Annotation with ID {review_create.annotation_id} not found")
            
            # Get the sample associated with the annotation
            sample = db.query(DataSample).filter(
                DataSample.id == annotation.sample_id
            ).first()
            
            if not sample:
                raise NotFoundError(f"Data sample for annotation {review_create.annotation_id} not found")
            
            # Verify sample is in annotated status
            if sample.status != SampleStatus.ANNOTATED:
                raise ConflictError(
                    f"Cannot review annotation for sample with status '{sample.status.value}'. "
                    f"Sample must be in 'annotated' status."
                )
            
            # Create review
            db_review = Review(
                annotation_id=review_create.annotation_id,
                reviewer_id=reviewer_id,
                decision=review_create.decision,
                feedback=review_create.feedback
            )
            
            db.add(db_review)
            
            # Update sample status based on review decision
            if review_create.decision == ReviewDecision.APPROVED:
                sample.status = SampleStatus.REVIEWED
                status_change = "reviewed"
            else:  # REJECTED
                sample.status = SampleStatus.PENDING
                status_change = "pending (rejected)"
            
            # Commit both changes atomically
            db.commit()
            db.refresh(db_review)
            
            logger.info(
                f"Review created: {db_review.id} for annotation {review_create.annotation_id} "
                f"by reviewer {reviewer_id}. Decision: {review_create.decision.value}. "
                f"Sample status updated to {status_change}."
            )
            
            return db_review
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating review: {e}")
            raise ConflictError("Failed to create review due to database constraint")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating review: {e}")
            raise
    
    @staticmethod
    def get_review(db: Session, review_id: uuid.UUID) -> Review:
        """
        Get a review by ID.
        
        Args:
            db: Database session
            review_id: Review ID
            
        Returns:
            Review object
            
        Raises:
            NotFoundError: If review not found
        """
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundError(f"Review with ID {review_id} not found")
        return review
    
    @staticmethod
    def get_reviews(
        db: Session,
        annotation_id: Optional[uuid.UUID] = None,
        reviewer_id: Optional[uuid.UUID] = None,
        decision: Optional[ReviewDecision] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Get list of reviews with optional filtering.
        
        Args:
            db: Database session
            annotation_id: Optional filter by annotation ID
            reviewer_id: Optional filter by reviewer ID
            decision: Optional filter by decision
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of reviews
        """
        query = db.query(Review)
        
        if annotation_id:
            query = query.filter(Review.annotation_id == annotation_id)
        
        if reviewer_id:
            query = query.filter(Review.reviewer_id == reviewer_id)
        
        if decision:
            query = query.filter(Review.decision == decision)
        
        return query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_review(db: Session, review_id: uuid.UUID) -> None:
        """
        Delete a review.
        
        Args:
            db: Database session
            review_id: Review ID
            
        Raises:
            NotFoundError: If review not found
        """
        review = ReviewService.get_review(db, review_id)
        db.delete(review)
        db.commit()
        logger.info(f"Review deleted: {review_id}")
