from dataclasses import dataclass
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
    ) -> GameResponseDTO:
        game = await self._user_game_dao.create(
            user_id=user_id,
            name=name,
            state=state,
            is_favorite=is_favorite,
        )
        return GameResponseDTO(
            id=game.id,
            name=game.name,
            state=game.state,
            is_favorite=game.is_favorite,
        )
