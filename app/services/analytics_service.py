from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case
from app.models.data_sample import DataSample
from app.models.annotation import Annotation
from app.models.review import Review
from app.models.enums import SampleStatus, ReviewDecision
from app.schemas.analytics import AnalyticsResponse
from app.core.logging import logger


class AnalyticsService:
    @staticmethod
    def get_analytics(db: Session) -> AnalyticsResponse:
        """
        Get comprehensive analytics using efficient aggregate queries.
        
        This method uses a single query with aggregate functions to minimize
        database round trips and improve performance.
        
        Args:
            db: Database session
            
        Returns:
            AnalyticsResponse with all statistics
        """
        try:
            # Get sample counts by status in a single query using CASE statements
            sample_stats = db.query(
                func.count(DataSample.id).label('total'),
                func.sum(
                    case((DataSample.status == SampleStatus.PENDING, 1), else_=0)
                ).label('pending'),
                func.sum(
                    case((DataSample.status == SampleStatus.ANNOTATED, 1), else_=0)
                ).label('annotated'),
                func.sum(
                    case((DataSample.status == SampleStatus.REVIEWED, 1), else_=0)
                ).label('reviewed')
            ).first()
            
            total_samples = sample_stats.total or 0
            pending_samples = int(sample_stats.pending or 0)
            annotated_samples = int(sample_stats.annotated or 0)
            reviewed_samples = int(sample_stats.reviewed or 0)
            
            # Get review statistics in a single query using CASE statements
            review_stats = db.query(
                func.count(Review.id).label('total_reviews'),
                func.sum(
                    case((Review.decision == ReviewDecision.APPROVED, 1), else_=0)
                ).label('approved'),
                func.sum(
                    case((Review.decision == ReviewDecision.REJECTED, 1), else_=0)
                ).label('rejected')
            ).first()
            
            total_reviews = review_stats.total_reviews or 0
            approved_count = review_stats.approved or 0
            rejected_count = review_stats.rejected or 0
            
            # Calculate approval and rejection rates
            if total_reviews > 0:
                approval_rate = round((approved_count / total_reviews) * 100, 2)
                rejection_rate = round((rejected_count / total_reviews) * 100, 2)
            else:
                approval_rate = 0.0
                rejection_rate = 0.0
            
            # Get unique annotator count using distinct
            annotator_count = db.query(
                func.count(distinct(Annotation.annotator_id))
            ).scalar() or 0
            
            logger.info(
                f"Analytics retrieved: {total_samples} samples, "
                f"{approval_rate}% approval rate, {annotator_count} annotators"
            )
            
            return AnalyticsResponse(
                total_samples=total_samples,
                pending_samples=pending_samples,
                annotated_samples=annotated_samples,
                reviewed_samples=reviewed_samples,
                approval_rate=approval_rate,
                rejection_rate=rejection_rate,
                annotator_contribution_count=annotator_count
            )
            
        except Exception as e:
            logger.error(f"Error retrieving analytics: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_project_analytics(db: Session, project_id) -> dict:
        """
        Get analytics for a specific project.
        
        Args:
            db: Database session
            project_id: Project UUID as string
            
        Returns:
            Dictionary with project-specific analytics
        """
        try:
            # Get sample counts by status for the project using CASE statements
            sample_stats = db.query(
                func.count(DataSample.id).label('total'),
                func.sum(
                    case((DataSample.status == SampleStatus.PENDING, 1), else_=0)
                ).label('pending'),
                func.sum(
                    case((DataSample.status == SampleStatus.ANNOTATED, 1), else_=0)
                ).label('annotated'),
                func.sum(
                    case((DataSample.status == SampleStatus.REVIEWED, 1), else_=0)
                ).label('reviewed')
            ).filter(
                DataSample.project_id == project_id
            ).first()
            
            # Get review statistics for annotations in this project using CASE statements
            review_stats = db.query(
                func.count(Review.id).label('total_reviews'),
                func.sum(
                    case((Review.decision == ReviewDecision.APPROVED, 1), else_=0)
                ).label('approved'),
                func.sum(
                    case((Review.decision == ReviewDecision.REJECTED, 1), else_=0)
                ).label('rejected')
            ).join(
                Annotation, Review.annotation_id == Annotation.id
            ).join(
                DataSample, Annotation.sample_id == DataSample.id
            ).filter(
                DataSample.project_id == project_id
            ).first()
            
            total_samples = sample_stats.total or 0
            total_reviews = review_stats.total_reviews or 0
            approved_count = int(review_stats.approved or 0)
            rejected_count = int(review_stats.rejected or 0)
            
            approval_rate = round((approved_count / total_reviews) * 100, 2) if total_reviews > 0 else 0.0
            rejection_rate = round((rejected_count / total_reviews) * 100, 2) if total_reviews > 0 else 0.0
            
            # Get unique annotator count for this project
            annotator_count = db.query(
                func.count(distinct(Annotation.annotator_id))
            ).join(
                DataSample, Annotation.sample_id == DataSample.id
            ).filter(
                DataSample.project_id == project_id
            ).scalar() or 0
            
            return {
                "total_samples": total_samples,
                "pending_samples": int(sample_stats.pending or 0),
                "annotated_samples": int(sample_stats.annotated or 0),
                "reviewed_samples": int(sample_stats.reviewed or 0),
                "approval_rate": approval_rate,
                "rejection_rate": rejection_rate,
                "annotator_contribution_count": annotator_count
            }
            
        except Exception as e:
            logger.error(f"Error retrieving project analytics: {e}", exc_info=True)
            raise
