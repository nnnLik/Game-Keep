"""add activity and activity_vote

Revision ID: a1b2c3d4e5f6
Revises: 33af5c966168
Create Date: 2026-03-15 17:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "33af5c966168"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activity",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("action_type", sa.String(32), nullable=False),
        sa.Column("user_game_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_game_id"], ["user_game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("activity", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_activity_user_id"), ["user_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_activity_user_game_id"), ["user_game_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_activity_created_at"), ["created_at"], unique=False)

    op.create_table(
        "activity_vote",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("is_like", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activity.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("activity_id", "user_id", "is_like", name="uq_activity_user_is_like"),
    )
    with op.batch_alter_table("activity_vote", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_activity_vote_activity_id"), ["activity_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_activity_vote_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("activity_vote", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_activity_vote_user_id"))
        batch_op.drop_index(batch_op.f("ix_activity_vote_activity_id"))
    op.drop_table("activity_vote")
    with op.batch_alter_table("activity", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_activity_created_at"))
        batch_op.drop_index(batch_op.f("ix_activity_user_game_id"))
        batch_op.drop_index(batch_op.f("ix_activity_user_id"))
    op.drop_table("activity")
