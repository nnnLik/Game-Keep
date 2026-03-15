from dataclasses import dataclass
from datetime import date
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
        image_url: str | None = None,
        steam_app_id: str | None = None,
        genres: list[str] | None = None,
        developers: list[str] | None = None,
        publishers: list[str] | None = None,
        release_date: str | None = None,
        note: str | None = None,
        date_started: date | None = None,
        date_finished: date | None = None,
        hours_played: float | None = None,
    ) -> UserGame:
        game = UserGame(
            user_id=user_id,
            name=name,
            state=state,
            is_favorite=is_favorite,
            image_url=image_url,
            steam_app_id=steam_app_id,
            genres=genres or [],
            developers=developers or [],
            publishers=publishers or [],
            release_date=release_date,
            note=note,
            date_started=date_started,
            date_finished=date_finished,
            hours_played=round(hours_played, 1) if hours_played is not None else None,
        )
        self._session.add(game)
        await self._session.flush()
        await self._session.refresh(game)
        return game
