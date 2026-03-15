from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db import get_db
from services.games.get_game_service import GetGameService

router = APIRouter(prefix='/games', tags=['games'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.get('/{game_id}')
async def get_game(game_id: int, session: SessionDep):
    service = GetGameService.build(session)
    result = await service.execute(game_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found',
        )
    return result
