from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.mixins import IntPkMixin


class GameComment(Base, IntPkMixin):
    __tablename__ = 'game_comment'
    game_id: Mapped[int] = mapped_column(
        ForeignKey('user_game.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey('game_comment.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    text: Mapped[str] = mapped_column(String(200), nullable=False)

    game = relationship('UserGame', back_populates='comments')
    user = relationship('User', back_populates='game_comments')
    parent = relationship(
        'GameComment',
        remote_side='GameComment.id',
        back_populates='children',
    )
    children = relationship('GameComment', back_populates='parent')
    votes = relationship(
        'GameCommentVote',
        back_populates='comment',
        cascade='all, delete-orphan',
    )
