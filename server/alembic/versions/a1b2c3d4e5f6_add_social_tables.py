"""add social_accounts and social_posts tables

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-02-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'social_accounts' in inspector.get_table_names() or 'social_posts' in inspector.get_table_names():
        return

    # create enum type for social post status
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE socialpoststatus AS ENUM ('pending', 'posted', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create social_accounts table
    op.execute("""
        CREATE TABLE social_accounts (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL,
            platform VARCHAR(50) NOT NULL,
            platform_user_id VARCHAR(255) NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at TIMESTAMP WITH TIME ZONE,
            scopes VARCHAR(512),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create social_posts table
    op.execute("""
        CREATE TABLE social_posts (
            id SERIAL PRIMARY KEY,
            pipeline_run_id VARCHAR(255),
            social_account_id INTEGER,
            platform VARCHAR(50) NOT NULL,
            status socialpoststatus NOT NULL,
            platform_post_id VARCHAR(255),
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(run_id),
            FOREIGN KEY (social_account_id) REFERENCES social_accounts(id) ON DELETE SET NULL
        )
    """)

    # Indexes
    op.create_index(op.f('ix_social_accounts_user_id'), 'social_accounts', ['user_id'], unique=False)
    op.create_index(op.f('ix_social_accounts_platform'), 'social_accounts', ['platform'], unique=False)
    op.create_index(op.f('ix_social_posts_pipeline_run_id'), 'social_posts', ['pipeline_run_id'], unique=False)
    op.create_index(op.f('ix_social_posts_social_account_id'), 'social_posts', ['social_account_id'], unique=False)
    op.create_index(op.f('ix_social_posts_platform'), 'social_posts', ['platform'], unique=False)
    op.create_index(op.f('ix_social_posts_status'), 'social_posts', ['status'], unique=False)


def downgrade() -> None:
    # drop indexes
    op.drop_index(op.f('ix_social_posts_status'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_platform'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_social_account_id'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_pipeline_run_id'), table_name='social_posts')
    op.drop_index(op.f('ix_social_accounts_platform'), table_name='social_accounts')
    op.drop_index(op.f('ix_social_accounts_user_id'), table_name='social_accounts')

    # drop tables
    op.drop_table('social_posts')
    op.drop_table('social_accounts')

    # drop enum
    op.execute("""
        DO $$ BEGIN
            DROP TYPE IF EXISTS socialpoststatus;
        EXCEPTION
            WHEN undefined_object THEN null;
        END $$;
    """)
