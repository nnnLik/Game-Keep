from dataclasses import dataclass
from datetime import date
from typing import Self
from uuid import UUID

import constants.game
from daos.games.user_game_dao import UserGameDAO
from dtos.users import GameResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class CreateGameService:
    _user_game_dao: UserGameDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_game_dao=UserGameDAO.build(session))

    async def execute(
        self,
        user_id: UUID,
        name: str,
        state: constants.game.GameStateEnum,
        is_favorite: bool = False,
        image_url: str | None = None,
        steam_app_id: str | None = None,
        genres: list[dict[str, str]] | None = None,
        developers: list[str] | None = None,
        publishers: list[str] | None = None,
        release_date: str | None = None,
        note: str | None = None,
        date_started: date | None = None,
        date_finished: date | None = None,
        hours_played: float | None = None,
    ) -> GameResponseDTO:
        genres_unique: list[str] | None = None
        if genres:
            genres_unique = list(dict.fromkeys(g.get('description', '') for g in genres if g.get('description')))
        developers_unique = list(dict.fromkeys(developers)) if developers else None
        publishers_unique = list(dict.fromkeys(publishers)) if publishers else None

        game = await self._user_game_dao.create(
            user_id=user_id,
            name=name,
            state=state,
            is_favorite=is_favorite,
            image_url=image_url,
            steam_app_id=steam_app_id,
            genres=genres_unique,
            developers=developers_unique,
            publishers=publishers_unique,
            release_date=release_date,
            note=note,
            date_started=date_started,
            date_finished=date_finished,
            hours_played=round(hours_played, 1) if hours_played is not None else None,
        )
        genres_response = [{'id': str(i), 'description': s} for i, s in enumerate(game.genres or [])]
        return GameResponseDTO(
            id=game.id,
            name=game.name,
            image_url=game.image_url,
            steam_app_id=game.steam_app_id,
            state=game.state,
            is_favorite=game.is_favorite,
            genres=genres_response if genres_response else None,
            developers=game.developers,
            publishers=game.publishers,
            release_date=game.release_date,
            note=game.note,
            date_started=game.date_started,
            date_finished=game.date_finished,
            hours_played=game.hours_played,
        )
