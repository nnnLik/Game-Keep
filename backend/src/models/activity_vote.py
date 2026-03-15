from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.mixins import IntPkMixin


class ActivityVote(Base, IntPkMixin):
    __table_args__ = (
        UniqueConstraint("activity_id", "user_id", "is_like", name="uq_activity_user_is_like"),
    )

    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activity.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False)

    activity = relationship("Activity", back_populates="votes")
