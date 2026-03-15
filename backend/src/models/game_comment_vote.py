from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class GameCommentVote(Base):
    __tablename__ = 'game_comment_vote'
    __table_args__ = (
        UniqueConstraint('comment_id', 'user_id', 'is_like', name='uq_comment_user_is_like'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(
        ForeignKey('game_comment.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False)

    comment = relationship('GameComment', back_populates='votes')
