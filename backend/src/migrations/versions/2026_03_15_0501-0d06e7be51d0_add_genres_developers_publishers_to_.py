"""add genres developers publishers to user_game

Revision ID: 0d06e7be51d0
Revises: 41bf0c75c003
Create Date: 2026-03-15 05:01:01.018667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d06e7be51d0'
down_revision: Union[str, Sequence[str], None] = '41bf0c75c003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user_game', sa.Column('genres', sa.Text(), nullable=True))
    op.add_column('user_game', sa.Column('developers', sa.Text(), nullable=True))
    op.add_column('user_game', sa.Column('publishers', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user_game', 'publishers')
    op.drop_column('user_game', 'developers')
    op.drop_column('user_game', 'genres')
