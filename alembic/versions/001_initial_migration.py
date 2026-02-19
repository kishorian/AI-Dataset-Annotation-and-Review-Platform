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
    
    # Create users table (only if it doesn't exist)
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL,
            role userrole NOT NULL DEFAULT 'annotator',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)
    # Create indexes only if they don't exist
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_role ON users(role)")
    
    # Create projects table (only if it doesn't exist)
    op.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR NOT NULL,
            description TEXT,
            created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_projects_id ON projects(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_projects_name ON projects(name)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_project_created_by ON projects(created_by)")
    
    # Create data_samples table (only if it doesn't exist)
    op.execute("""
        CREATE TABLE IF NOT EXISTS data_samples (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            text_content TEXT NOT NULL,
            status samplestatus NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_samples_id ON data_samples(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_samples_project_id ON data_samples(project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_samples_status ON data_samples(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sample_project_id ON data_samples(project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sample_status ON data_samples(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sample_project_status ON data_samples(project_id, status)")
    
    # Create annotations table (only if it doesn't exist)
    op.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            sample_id UUID NOT NULL REFERENCES data_samples(id) ON DELETE CASCADE,
            annotator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            label annotationlabel NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_annotations_id ON annotations(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_annotations_sample_id ON annotations(sample_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_annotations_annotator_id ON annotations(annotator_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_annotations_label ON annotations(label)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_annotation_sample_id ON annotations(sample_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_annotation_annotator_id ON annotations(annotator_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_annotation_label ON annotations(label)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_annotation_sample_annotator ON annotations(sample_id, annotator_id)")
    
    # Create reviews table (only if it doesn't exist)
    op.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            annotation_id UUID NOT NULL REFERENCES annotations(id) ON DELETE CASCADE,
            reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            decision reviewdecision NOT NULL,
            feedback TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_id ON reviews(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_annotation_id ON reviews(annotation_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_reviewer_id ON reviews(reviewer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_decision ON reviews(decision)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_review_annotation_id ON reviews(annotation_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_review_reviewer_id ON reviews(reviewer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_review_decision ON reviews(decision)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_review_annotation_reviewer ON reviews(annotation_id, reviewer_id)")


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
