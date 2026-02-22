"""add pipeline assets table

Revision ID: e7f8a9b0c1d2
Revises: 4841502215e5
Create Date: 2026-01-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM


# revision identifiers, used by Alembic.
revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, Sequence[str], None] = '4841502215e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pipeline_assets table for storing file upload metadata"""
    
    # Check if table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'pipeline_assets' in inspector.get_table_names():
        return  # Table already exists, skip migration
    
    # Create enum types (only if they don't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE assetuploadstatus AS ENUM ('pending', 'uploaded', 'confirmed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE assetrole AS ENUM (
                'reference_image', 
                'reference_video', 
                'reference_audio', 
                'reference_document', 
                'reference_other'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create pipeline_assets table using raw SQL to avoid SQLAlchemy enum creation
    op.execute("""
        CREATE TABLE pipeline_assets (
            id SERIAL PRIMARY KEY,
            pipeline_id INTEGER NOT NULL,
            user_id UUID NOT NULL,
            filename VARCHAR(255) NOT NULL,
            content_type VARCHAR(100) NOT NULL,
            file_size BIGINT NOT NULL,
            s3_key VARCHAR(512) NOT NULL UNIQUE,
            s3_bucket VARCHAR(100) NOT NULL,
            role assetrole NOT NULL,
            upload_status assetuploadstatus NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            uploaded_at TIMESTAMP WITH TIME ZONE,
            FOREIGN KEY (pipeline_id) REFERENCES pipelines(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    op.create_index(op.f('ix_pipeline_assets_pipeline_id'), 'pipeline_assets', ['pipeline_id'], unique=False)
    op.create_index(op.f('ix_pipeline_assets_user_id'), 'pipeline_assets', ['user_id'], unique=False)
    op.create_index(op.f('ix_pipeline_assets_s3_key'), 'pipeline_assets', ['s3_key'], unique=True)
    op.create_index(op.f('ix_pipeline_assets_upload_status'), 'pipeline_assets', ['upload_status'], unique=False)


def downgrade() -> None:
    """Drop pipeline_assets table and enum types"""
    
    # Drop indexes
    op.drop_index(op.f('ix_pipeline_assets_upload_status'), table_name='pipeline_assets')
    op.drop_index(op.f('ix_pipeline_assets_s3_key'), table_name='pipeline_assets')
    op.drop_index(op.f('ix_pipeline_assets_user_id'), table_name='pipeline_assets')
    op.drop_index(op.f('ix_pipeline_assets_pipeline_id'), table_name='pipeline_assets')
    
    # Drop table
    op.drop_table('pipeline_assets')
    
    # Drop enum types (only if they exist)
    op.execute("""
        DO $$ BEGIN
            DROP TYPE IF EXISTS assetuploadstatus;
        EXCEPTION
            WHEN undefined_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            DROP TYPE IF EXISTS assetrole;
        EXCEPTION
            WHEN undefined_object THEN null;
        END $$;
    """)
