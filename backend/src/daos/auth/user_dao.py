from dataclasses import dataclass
from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


@dataclass
class UserDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_session=session)

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, username: str, password_hash: str) -> User:
        user = User(username=username, password=password_hash)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user
