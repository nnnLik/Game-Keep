"""add game_comment and game_comment_vote

Revision ID: 044f1422535e
Revises: 7170d80a9a47
Create Date: 2026-03-15 06:23:30.632994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '044f1422535e'
down_revision: Union[str, Sequence[str], None] = '7170d80a9a47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'game_comment',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('text', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['user_game.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['game_comment.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('game_comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_game_comment_game_id'), ['game_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_game_comment_parent_id'), ['parent_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_game_comment_user_id'), ['user_id'], unique=False)

    op.create_table(
        'game_comment_vote',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('is_like', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['comment_id'], ['game_comment.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('comment_id', 'user_id', 'is_like', name='uq_comment_user_is_like'),
    )
    with op.batch_alter_table('game_comment_vote', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_game_comment_vote_comment_id'), ['comment_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_game_comment_vote_user_id'), ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('game_comment_vote', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_game_comment_vote_user_id'))
        batch_op.drop_index(batch_op.f('ix_game_comment_vote_comment_id'))
    op.drop_table('game_comment_vote')
    with op.batch_alter_table('game_comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_game_comment_user_id'))
        batch_op.drop_index(batch_op.f('ix_game_comment_parent_id'))
        batch_op.drop_index(batch_op.f('ix_game_comment_game_id'))
    op.drop_table('game_comment')
