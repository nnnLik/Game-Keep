"""add view_count to user_game

Revision ID: 7170d80a9a47
Revises: f0061fa5153e
Create Date: 2026-03-15 06:19:54.961271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7170d80a9a47'
down_revision: Union[str, Sequence[str], None] = 'f0061fa5153e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'user_game',
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user_game', 'view_count')
