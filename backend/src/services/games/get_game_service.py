from dataclasses import dataclass
from typing import Self

from daos.games.user_game_dao import UserGameDAO
from dtos.games import GameDetailResponseDTO, GameOwnerDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GetGameService:
    _dao: UserGameDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_dao=UserGameDAO.build(session))

    def _genres_to_response(self, genres):
        if not genres:
            return None
        strings = [
            s if isinstance(s, str) else s.get('description', '')
            for s in genres
        ]
        return [
            {'id': str(i), 'description': s}
            for i, s in enumerate(strings)
            if s
        ] or None

    async def execute(self, game_id: int) -> GameDetailResponseDTO | None:
        game = await self._dao.get_by_id(game_id)
        if not game:
            return None
        await self._dao.increment_view_count(game)
        user = game.user
        return GameDetailResponseDTO(
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
            view_count=game.view_count,
            owner=GameOwnerDTO(
                username=user.username,
                tag=user.tag,
                avatar_url=user.avatar_url,
            ),
        )
