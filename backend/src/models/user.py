from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.mixins import UUIDPKMixin


class User(Base, UUIDPKMixin):
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tag: Mapped[str | None] = mapped_column(String(15), unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_registration_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    games = relationship('UserGame', back_populates='user', cascade='all, delete-orphan')
    game_comments = relationship(
        'GameComment',
        back_populates='user',
        cascade='all, delete-orphan',
    )
