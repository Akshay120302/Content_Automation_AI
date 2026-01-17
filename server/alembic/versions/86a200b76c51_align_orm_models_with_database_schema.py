"""align orm models with database schema

Revision ID: 86a200b76c51
Revises: d2d205cc1206
Create Date: 2026-01-17 14:26:49.520163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86a200b76c51'
down_revision: Union[str, Sequence[str], None] = 'd2d205cc1206'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
