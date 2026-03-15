"""user_game genres developers publishers default empty list

Revision ID: a579c82dfcba
Revises: 0d06e7be51d0
Create Date: 2026-03-15 05:08:35.258100

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a579c82dfcba'
down_revision: Union[str, Sequence[str], None] = '0d06e7be51d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE user_game SET genres = '[]' WHERE genres IS NULL")
    op.execute("UPDATE user_game SET developers = '[]' WHERE developers IS NULL")
    op.execute("UPDATE user_game SET publishers = '[]' WHERE publishers IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    pass
