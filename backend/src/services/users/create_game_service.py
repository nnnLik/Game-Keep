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
        image_url: str | None = None,
        steam_app_id: str | None = None,
    ) -> GameResponseDTO:
        game = await self._user_game_dao.create(
            user_id=user_id,
            name=name,
            state=state,
            is_favorite=is_favorite,
            image_url=image_url,
            steam_app_id=steam_app_id,
        )
        return GameResponseDTO(
            id=game.id,
            name=game.name,
            image_url=game.image_url,
            steam_app_id=game.steam_app_id,
            state=game.state,
            is_favorite=game.is_favorite,
        )
