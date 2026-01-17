"""add email verification tokens

Revision ID: 5659ffb77fb6
Revises: 86a200b76c51
Create Date: 2026-01-17 19:32:51.729734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5659ffb77fb6'
down_revision: Union[str, Sequence[str], None] = '86a200b76c51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
