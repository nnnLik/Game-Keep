from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import constants.game
from dtos.games import FetchSteamResponseDTO, GenreDTO
from dtos.users import (
    CreateGameRequestDTO,
    GameResponseDTO,
    UpdateGameFavoriteRequestDTO,
)
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.games.fetch_steam_game_service import FetchSteamGameService
from services.users.create_game_service import CreateGameService
from services.users.my_games_service import MyGamesService
from services.users.update_game_favorite_service import UpdateGameFavoriteService

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
            genres=[GenreDTO(id=g.id, description=g.description) for g in result.genres],
            developers=result.developers,
            publishers=result.publishers,
            release_date=result.release_date,
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
        state=constants.game.GameStateEnum(data.state),
        is_favorite=data.is_favorite,
        image_url=data.image_url,
        steam_app_id=data.steam_app_id,
        genres=data.genres,
        developers=data.developers,
        publishers=data.publishers,
        release_date=data.release_date,
        note=data.note,
        date_started=data.date_started,
        date_finished=data.date_finished,
        hours_played=data.hours_played,
    )


@router.patch('/games/{game_id}', response_model=GameResponseDTO)
async def update_game_favorite(
    game_id: int,
    data: UpdateGameFavoriteRequestDTO,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> GameResponseDTO:
    result = await UpdateGameFavoriteService.build(session).execute(
        game_id=game_id,
        user_id=current_user.id,
        is_favorite=data.is_favorite,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found',
        )
    return result


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
