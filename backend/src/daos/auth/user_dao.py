from dataclasses import dataclass
from typing import Self
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


@dataclass
class UserDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_session=session)

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_tag(self, tag: str) -> User | None:
        tag_lower = tag.strip().lower()
        result = await self._session.execute(select(User).where(User.tag == tag_lower))
        return result.scalar_one_or_none()

    async def create(
        self,
        username: str,
        tag: str,
        email: str,
        password_hash: str,
    ) -> User:
        user = User(
            username=username,
            tag=tag.strip().lower(),
            email=email,
            password=password_hash,
            is_registration_complete=True,
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def create_minimal(self, email: str, password_hash: str) -> User:
        user = User(
            username=None,
            tag=None,
            email=email,
            password=password_hash,
            is_registration_complete=False,
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_profile(
        self,
        user_id: UUID,
        username: str,
        tag: str,
        avatar_url: str | None = None,
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.username = username
        user.tag = tag.strip().lower()
        if avatar_url is not None:
            user.avatar_url = avatar_url
        user.is_registration_complete = True
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_banner(self, user_id: UUID, banner_url: str) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.banner_url = banner_url
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_avatar(self, user_id: UUID, avatar_url: str) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.avatar_url = avatar_url
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def clear_banner(self, user_id: UUID) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.banner_url = None
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_list_with_games_count(
        self,
        limit: int,
        cursor_games_count: int | None = None,
        cursor_user_id: UUID | None = None,
    ) -> list[tuple[User, int]]:
        from models.user_game import UserGame

        subq = (
            select(User.id, func.count(UserGame.id).label('games_count'))
            .select_from(User)
            .join(UserGame, User.id == UserGame.user_id)
            .where(User.is_registration_complete.is_(True))
            .group_by(User.id)
            .having(func.count(UserGame.id) >= 1)
        ).subquery()

        stmt = (
            select(User, subq.c.games_count)
            .join(subq, User.id == subq.c.id)
            .order_by(subq.c.games_count.desc(), User.id.asc())
        )

        if cursor_games_count is not None and cursor_user_id is not None:
            stmt = stmt.where(
                (subq.c.games_count < cursor_games_count)
                | ((subq.c.games_count == cursor_games_count) & (User.id > cursor_user_id))
            )

        stmt = stmt.limit(limit + 1)
        result = await self._session.execute(stmt)
        return list(result.all())
