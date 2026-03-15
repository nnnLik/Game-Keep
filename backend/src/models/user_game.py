from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, String
from sqlalchemy.types import JSON
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
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    steam_app_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    developers: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    publishers: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    release_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    date_started: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_finished: Mapped[date | None] = mapped_column(Date, nullable=True)
    hours_played: Mapped[float | None] = mapped_column(Float, nullable=True)
    state: Mapped[constants.game.GameStateEnum] = mapped_column(
        Enum(
            constants.game.GameStateEnum,
            values_callable=lambda x: [e.value for e in x],
            create_constraint=True,
            native_enum=False,
        ),
        nullable=False,
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    view_count: Mapped[int] = mapped_column(default=0, nullable=False)

    user = relationship('User', back_populates='games')
