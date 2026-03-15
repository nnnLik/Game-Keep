from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import constants.game
from dtos.games import FetchSteamResponseDTO
from dtos.users import CreateGameRequestDTO, GameResponseDTO
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.games.fetch_steam_game_service import FetchSteamGameService
from services.users.create_game_service import CreateGameService
from services.users.my_games_service import MyGamesService

router = APIRouter(prefix='/users/me', tags=['games'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post('/games/fetch-steam', response_model=FetchSteamResponseDTO)
async def fetch_steam_game(
    _: CurrentUserDep,
    steam_url: str = Body(embed=True),
) -> FetchSteamResponseDTO:
    service = FetchSteamGameService.build()
    try:
        result = service.execute(steam_url.strip())
        return FetchSteamResponseDTO(
            name=result.name,
            image_url=result.image_url,
            steam_app_id=result.steam_app_id,
        )
    except FetchSteamGameService.InvalidSteamUrlError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except FetchSteamGameService.GameNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post('/games', response_model=GameResponseDTO)
async def create_game(
    data: CreateGameRequestDTO,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> GameResponseDTO:
    return await CreateGameService.build(session).execute(
        user_id=current_user.id,
        name=data.name,
        state=data.state,
        is_favorite=data.is_favorite,
        image_url=data.image_url,
        steam_app_id=data.steam_app_id,
    )


@router.get('/games', response_model=list[GameResponseDTO])
async def my_games(
    current_user: CurrentUserDep,
    session: SessionDep,
    state: constants.game.GameStateEnum | None = None,
    is_favorite: bool | None = None,
) -> list[GameResponseDTO]:
    return await MyGamesService.build(session).execute(
        user_id=current_user.id,
        state=state,
        is_favorite=is_favorite,
    )
