from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base
from models.mixins import UUIDPKMixin


class User(Base, UUIDPKMixin):
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    tag: Mapped[str] = mapped_column(String(15), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
