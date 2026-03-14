from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.games.user_game_dao import UserGameDAO
from dtos.users import GameResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class MyGamesService:
    _user_game_dao: UserGameDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_game_dao=UserGameDAO.build(session))

    async def execute(
        self,
        user_id: UUID,
        state: str | None = None,
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
                state=g.state,
                is_favorite=g.is_favorite,
            )
            for g in games
        ]
