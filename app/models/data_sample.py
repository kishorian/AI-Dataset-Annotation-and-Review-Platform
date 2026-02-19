from sqlalchemy import Column, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app.models.enums import SampleStatus


class DataSample(Base):
    __tablename__ = "data_samples"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    text_content = Column(Text, nullable=False)
    # Use Postgres enum values (e.g. "pending") instead of names (e.g. "PENDING")
    status = Column(
        PGEnum(
            SampleStatus,
            name="samplestatus",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            create_type=False,
        ),
        nullable=False,
        default=SampleStatus.PENDING,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="data_samples")
    annotations = relationship("Annotation", back_populates="sample", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_sample_project_id", "project_id"),
        Index("idx_sample_status", "status"),
        Index("idx_sample_project_status", "project_id", "status"),
    )
