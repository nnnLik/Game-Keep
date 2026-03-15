from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from constants.activity import ActivityActionType
from models.base import Base
from models.mixins import IntPkMixin


class Activity(Base, IntPkMixin):
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[ActivityActionType] = mapped_column(
        Enum(
            ActivityActionType,
            values_callable=lambda x: [e.value for e in x],
            create_constraint=True,
            native_enum=False,
        ),
        nullable=False,
    )
    user_game_id: Mapped[int] = mapped_column(
        ForeignKey("user_game.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="activities")
    user_game = relationship("UserGame", back_populates="activities")
    votes = relationship(
        "ActivityVote",
        back_populates="activity",
        cascade="all, delete-orphan",
    )
