from dataclasses import dataclass
from typing import Self
from uuid import UUID

import constants.game
from daos.games.user_game_dao import UserGameDAO
from dtos.users import GameResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class MyGamesService:
    _user_game_dao: UserGameDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_game_dao=UserGameDAO.build(session))

    def _genres_to_response(
        self,
        genres: list[str] | list[dict[str, str]] | None,
    ) -> list[dict[str, str]] | None:
        if not genres:
            return None
        strings = [s if isinstance(s, str) else s.get('description', '') for s in genres]
        result = [{'id': str(i), 'description': s} for i, s in enumerate(strings) if s]
        return result or None

    async def execute(
        self,
        user_id: UUID,
        state: constants.game.GameStateEnum | None = None,
        is_favorite: bool | None = None,
    ) -> list[GameResponseDTO]:
        games = await self._user_game_dao.get_by_user(
            user_id,
            state=state,
            is_favorite=is_favorite,
        )
        return [
            GameResponseDTO(
                id=g.id,
                name=g.name,
                image_url=g.image_url,
                steam_app_id=g.steam_app_id,
                state=g.state,
                is_favorite=g.is_favorite,
                genres=self._genres_to_response(g.genres),
                developers=g.developers,
                publishers=g.publishers,
            )
            for g in games
        ]
