from sqlalchemy import Column, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app.models.enums import AnnotationLabel


class Annotation(Base):
    __tablename__ = "annotations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("data_samples.id", ondelete="CASCADE"), nullable=False, index=True)
    annotator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Use Postgres enum values (e.g. "positive") instead of names (e.g. "POSITIVE")
    label = Column(
        PGEnum(
            AnnotationLabel,
            name="annotationlabel",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            create_type=False,
        ),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    sample = relationship("DataSample", back_populates="annotations")
    annotator = relationship("User", back_populates="annotations")
    reviews = relationship("Review", back_populates="annotation", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_annotation_sample_id", "sample_id"),
        Index("idx_annotation_annotator_id", "annotator_id"),
        Index("idx_annotation_label", "label"),
        Index("idx_annotation_sample_annotator", "sample_id", "annotator_id"),
    )
