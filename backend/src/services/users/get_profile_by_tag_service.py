from dataclasses import dataclass
from typing import Self

from daos.auth.user_dao import UserDAO
from daos.games.user_game_dao import UserGameDAO
from dtos.users import GameResponseDTO, ProfileByTagResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GetProfileByTagService:
    _user_dao: UserDAO
    _user_game_dao: UserGameDAO

    class GetProfileByTagServiceError(Exception):
        pass

    class UserNotFoundError(GetProfileByTagServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_dao=UserDAO.build(session),
            _user_game_dao=UserGameDAO.build(session),
        )

    def _genres_to_response(
        self,
        genres: list[str] | list[dict[str, str]] | None,
    ) -> list[dict[str, str]] | None:
        if not genres:
            return None
        strings = [s if isinstance(s, str) else s.get('description', '') for s in genres]
        result = [{'id': str(i), 'description': s} for i, s in enumerate(strings) if s]
        return result or None

    async def execute(self, tag: str) -> ProfileByTagResponseDTO:
        user = await self._user_dao.get_by_tag(tag)
        if not user:
            raise self.UserNotFoundError

        games = await self._user_game_dao.get_by_user(user.id)
        games_dto = [
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
                release_date=g.release_date,
                note=g.note,
                date_started=g.date_started,
                date_finished=g.date_finished,
                hours_played=g.hours_played,
            )
            for g in games
        ]

        return {
            'username': user.username,
            'tag': user.tag,
            'avatar_url': user.avatar_url,
            'banner_url': user.banner_url,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'games': [g.model_dump() for g in games_dto],
        }
