from dataclasses import dataclass
from datetime import date
from typing import Self
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import constants.game
from models.user_game import UserGame


@dataclass
class UserGameDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_session=session)

    async def get_by_id(self, game_id: int) -> UserGame | None:
        stmt = (
            select(UserGame)
            .options(selectinload(UserGame.user))
            .where(UserGame.id == game_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_view_count(self, game: UserGame) -> None:
        game.view_count += 1
        await self._session.flush()

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

    async def update(
        self,
        game_id: int,
        user_id: UUID,
        **kwargs: object,
    ) -> UserGame | None:
        stmt = select(UserGame).where(
            UserGame.id == game_id,
            UserGame.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        game = result.scalar_one_or_none()
        if game is None:
            return None
        if 'name' in kwargs:
            game.name = kwargs['name']
        if 'state' in kwargs:
            game.state = kwargs['state']
        if 'is_favorite' in kwargs:
            game.is_favorite = kwargs['is_favorite']
        if 'image_url' in kwargs:
            game.image_url = kwargs['image_url']
        if 'steam_app_id' in kwargs:
            game.steam_app_id = kwargs['steam_app_id']
        if 'genres' in kwargs:
            game.genres = kwargs['genres'] or []
        if 'developers' in kwargs:
            game.developers = kwargs['developers'] or []
        if 'publishers' in kwargs:
            game.publishers = kwargs['publishers'] or []
        if 'release_date' in kwargs:
            game.release_date = kwargs['release_date']
        if 'note' in kwargs:
            game.note = kwargs['note']
        if 'date_started' in kwargs:
            game.date_started = kwargs['date_started']
        if 'date_finished' in kwargs:
            game.date_finished = kwargs['date_finished']
        if 'hours_played' in kwargs:
            h = kwargs['hours_played']
            game.hours_played = round(h, 1) if h is not None else None
        await self._session.flush()
        await self._session.refresh(game)
        return game

    async def delete(self, game_id: int, user_id: UUID) -> bool:
        stmt = select(UserGame).where(
            UserGame.id == game_id,
            UserGame.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        game = result.scalar_one_or_none()
        if game is None:
            return False
        await self._session.delete(game)
        await self._session.flush()
        return True

    async def update_is_favorite(
        self, game_id: int, user_id: UUID, is_favorite: bool
    ) -> UserGame | None:
        stmt = select(UserGame).where(
            UserGame.id == game_id,
            UserGame.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        game = result.scalar_one_or_none()
        if game is None:
            return None
        game.is_favorite = is_favorite
        await self._session.flush()
        await self._session.refresh(game)
        return game
