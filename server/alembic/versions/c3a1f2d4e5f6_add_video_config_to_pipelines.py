"""add video config to pipelines

Revision ID: c3a1f2d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c3a1f2d4e5f6"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pipelines", sa.Column("video_provider", sa.String(), nullable=True))
    op.add_column("pipelines", sa.Column("video_model", sa.String(), nullable=True))
    op.add_column("pipelines", sa.Column("video_duration_seconds", sa.Integer(), nullable=True))
    op.add_column("pipelines", sa.Column("video_aspect_ratio", sa.String(), nullable=True))
    op.add_column("pipelines", sa.Column("video_fps", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("pipelines", "video_fps")
    op.drop_column("pipelines", "video_aspect_ratio")
    op.drop_column("pipelines", "video_duration_seconds")
    op.drop_column("pipelines", "video_model")
    op.drop_column("pipelines", "video_provider")
