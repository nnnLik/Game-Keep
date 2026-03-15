from dataclasses import dataclass
from typing import Self
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import constants.game
from models.user_game import UserGame


@dataclass
class UserGameDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_session=session)

    async def get_by_user(
        self,
        user_id: UUID,
        state: constants.game.GameStateEnum | None = None,
        is_favorite: bool | None = None,
    ) -> list[UserGame]:
        stmt = select(UserGame).where(UserGame.user_id == user_id)
        if state is not None:
            stmt = stmt.where(UserGame.state == state)
        if is_favorite is not None:
            stmt = stmt.where(UserGame.is_favorite == is_favorite)
        stmt = stmt.order_by(UserGame.id.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        user_id: UUID,
        name: str,
        state: constants.game.GameStateEnum,
        is_favorite: bool = False,
    ) -> UserGame:

        game = UserGame(
            user_id=user_id,
            name=name,
            state=state,
            is_favorite=is_favorite,
        )
        self._session.add(game)
        await self._session.flush()
        await self._session.refresh(game)
        return game
