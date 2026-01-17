"""switch users id from integer to uuidv7

Revision ID: d2d205cc1206
Revises: b81badfff4c7
Create Date: 2026-01-17 13:17:36.830814

"""
# from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
# revision: str = 'd2d205cc1206'
# down_revision: Union[str, Sequence[str], None] = 'b81badfff4c7'
# branch_labels: Union[str, Sequence[str], None] = None
# depends_on: Union[str, Sequence[str], None] = None

revision: str = 'd2d205cc1206'
down_revision = 'b81badfff4c7'
branch_labels = None
depends_on = None


# def upgrade() -> None:
#     """Upgrade schema."""
#     pass

def upgrade():
    # 1. Drop foreign key constraints FIRST
    op.drop_constraint("subscriptions_user_id_fkey", "subscriptions", type_="foreignkey")
    op.drop_constraint("refresh_tokens_user_id_fkey", "refresh_tokens", type_="foreignkey")
    op.drop_constraint("oauth_accounts_user_id_fkey", "oauth_accounts", type_="foreignkey")

    # 2. Drop FK columns
    op.drop_column("subscriptions", "user_id")
    op.drop_column("refresh_tokens", "user_id")
    op.drop_column("oauth_accounts", "user_id")

    # 3. Drop users.id
    op.drop_column("users", "id")

    # 4. Recreate users.id as UUID
    op.add_column(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            # primary_key=True,
            nullable=False,
        ),
    )

    # 5. This is the missing piece
    op.create_primary_key(
        "users_pkey",
        "users",
        ["id"],
    )

    # 5. Recreate FK columns as UUID
    op.add_column(
        "subscriptions",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
    )
    op.add_column(
        "oauth_accounts",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
    )

    # 6. Recreate foreign keys
    op.create_foreign_key(
        "subscriptions_user_id_fkey",
        "subscriptions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "oauth_accounts_user_id_fkey",
        "oauth_accounts",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    raise RuntimeError("Downgrade not supported for UUID migration")


# def downgrade() -> None:
#     """Downgrade schema."""
#     pass
