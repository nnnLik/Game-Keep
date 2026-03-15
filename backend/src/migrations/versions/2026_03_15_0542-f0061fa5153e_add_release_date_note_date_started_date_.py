"""add release_date note date_started date_finished hours_played to user_game

Revision ID: f0061fa5153e
Revises: 7ef9063a1a10
Create Date: 2026-03-15 05:42:40.255157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0061fa5153e'
down_revision: Union[str, Sequence[str], None] = '7ef9063a1a10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user_game', sa.Column('release_date', sa.String(64), nullable=True))
    op.add_column('user_game', sa.Column('note', sa.String(512), nullable=True))
    op.add_column('user_game', sa.Column('date_started', sa.Date(), nullable=True))
    op.add_column('user_game', sa.Column('date_finished', sa.Date(), nullable=True))
    op.add_column('user_game', sa.Column('hours_played', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user_game', 'hours_played')
    op.drop_column('user_game', 'date_finished')
    op.drop_column('user_game', 'date_started')
    op.drop_column('user_game', 'note')
    op.drop_column('user_game', 'release_date')
