from uuid import UUID

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

import constants.game
from models.base import Base
from models.mixins import IntPkMixin


class UserGame(Base, IntPkMixin):
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[constants.game.GameStateEnum] = mapped_column(
        Enum(
            constants.game.GameStateEnum,
            create_constraint=True,
            native_enum=False,
        ),
        nullable=False,
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship('User', back_populates='games')
