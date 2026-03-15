from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.games.user_game_dao import UserGameDAO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class DeleteGameService:
    _user_game_dao: UserGameDAO

    class GameNotFoundError(Exception):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_game_dao=UserGameDAO.build(session))

    async def execute(self, game_id: int, user_id: UUID) -> None:
        deleted = await self._user_game_dao.delete(game_id, user_id)
        if not deleted:
            raise self.GameNotFoundError
