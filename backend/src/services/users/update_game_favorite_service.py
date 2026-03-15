from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.games.user_game_dao import UserGameDAO
from dtos.users import GameResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class UpdateGameFavoriteService:
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
        game_id: int,
        user_id: UUID,
        is_favorite: bool,
    ) -> GameResponseDTO | None:
        game = await self._user_game_dao.update_is_favorite(
            game_id, user_id, is_favorite
        )
        if game is None:
            return None
        return GameResponseDTO(
            id=game.id,
            name=game.name,
            image_url=game.image_url,
            steam_app_id=game.steam_app_id,
            state=game.state,
            is_favorite=game.is_favorite,
            genres=self._genres_to_response(game.genres),
            developers=game.developers,
            publishers=game.publishers,
            release_date=game.release_date,
            note=game.note,
            date_started=game.date_started,
            date_finished=game.date_finished,
            hours_played=game.hours_played,
        )
