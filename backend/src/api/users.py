from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import constants.game
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from dtos.users import GameResponseDTO, MeResponseDTO
from services.users.me_service import MeService
from services.users.my_games_service import MyGamesService

router = APIRouter(prefix='/users', tags=['users'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

@router.get('/me', response_model=MeResponseDTO)
async def me(current_user: CurrentUserDep, session: SessionDep) -> MeResponseDTO:
    return await MeService.build(session).execute(current_user.id)


@router.get('/me/games', response_model=list[GameResponseDTO])
async def my_games(
    current_user: CurrentUserDep,
    session: SessionDep,
    state: constants.game.GameStateEnum | None = None,
    is_favorite: bool | None = None,
) -> list[GameResponseDTO]:
    return await MyGamesService.build(session).execute(
        current_user.id,
        state=state,
        is_favorite=is_favorite,
    )
