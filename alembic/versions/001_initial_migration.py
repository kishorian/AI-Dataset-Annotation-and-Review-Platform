"""Initial migration: create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-19 08:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types (only if they don't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('admin', 'annotator', 'reviewer');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE samplestatus AS ENUM ('pending', 'annotated', 'reviewed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE annotationlabel AS ENUM ('positive', 'negative', 'neutral');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE reviewdecision AS ENUM ('approved', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'annotator', 'reviewer', name='userrole'), nullable=False, server_default='annotator'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_projects_id', 'projects', ['id'])
    op.create_index('ix_projects_name', 'projects', ['name'])
    op.create_index('idx_project_created_by', 'projects', ['created_by'])
    
    # Create data_samples table
    op.create_table(
        'data_samples',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'annotated', 'reviewed', name='samplestatus'), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_data_samples_id', 'data_samples', ['id'])
    op.create_index('ix_data_samples_project_id', 'data_samples', ['project_id'])
    op.create_index('ix_data_samples_status', 'data_samples', ['status'])
    op.create_index('idx_sample_project_id', 'data_samples', ['project_id'])
    op.create_index('idx_sample_status', 'data_samples', ['status'])
    op.create_index('idx_sample_project_status', 'data_samples', ['project_id', 'status'])
    
    # Create annotations table
    op.create_table(
        'annotations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('sample_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('annotator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('label', postgresql.ENUM('positive', 'negative', 'neutral', name='annotationlabel'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sample_id'], ['data_samples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['annotator_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_annotations_id', 'annotations', ['id'])
    op.create_index('ix_annotations_sample_id', 'annotations', ['sample_id'])
    op.create_index('ix_annotations_annotator_id', 'annotations', ['annotator_id'])
    op.create_index('ix_annotations_label', 'annotations', ['label'])
    op.create_index('idx_annotation_sample_id', 'annotations', ['sample_id'])
    op.create_index('idx_annotation_annotator_id', 'annotations', ['annotator_id'])
    op.create_index('idx_annotation_label', 'annotations', ['label'])
    op.create_index('idx_annotation_sample_annotator', 'annotations', ['sample_id', 'annotator_id'])
    
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('annotation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('decision', postgresql.ENUM('approved', 'rejected', name='reviewdecision'), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'])
    op.create_index('ix_reviews_annotation_id', 'reviews', ['annotation_id'])
    op.create_index('ix_reviews_reviewer_id', 'reviews', ['reviewer_id'])
    op.create_index('ix_reviews_decision', 'reviews', ['decision'])
    op.create_index('idx_review_annotation_id', 'reviews', ['annotation_id'])
    op.create_index('idx_review_reviewer_id', 'reviews', ['reviewer_id'])
    op.create_index('idx_review_decision', 'reviews', ['decision'])
    op.create_index('idx_review_annotation_reviewer', 'reviews', ['annotation_id', 'reviewer_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('reviews')
    op.drop_table('annotations')
    op.drop_table('data_samples')
    op.drop_table('projects')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS reviewdecision')
    op.execute('DROP TYPE IF EXISTS annotationlabel')
    op.execute('DROP TYPE IF EXISTS samplestatus')
    op.execute('DROP TYPE IF EXISTS userrole')
