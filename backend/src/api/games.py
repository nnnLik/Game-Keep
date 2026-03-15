from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from daos.games.user_game_dao import UserGameDAO
from dtos.games import CreateCommentRequestDTO
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.games.create_comment_service import CreateCommentService
from services.games.get_comments_service import GetCommentsService
from services.games.get_game_service import GetGameService
from services.games.vote_comment_service import VoteCommentService

router = APIRouter(prefix='/games', tags=['games'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


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


@router.get('/{game_id}/comments')
async def get_comments(
    game_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    game = await UserGameDAO.build(session).get_by_id(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found',
        )
    service = GetCommentsService.build(session, current_user.id)
    return await service.execute(game_id)


@router.post('/{game_id}/comments')
async def create_comment(
    game_id: int,
    data: CreateCommentRequestDTO,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    service = CreateCommentService.build(session)
    comment_id, err = await service.execute(
        game_id=game_id,
        user_id=current_user.id,
        text=data.text,
        parent_id=data.parent_id,
    )
    if err == 'not_found':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found',
        )
    if err == 'bad_request':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid text (1-200 chars) or parent',
        )
    return {'id': comment_id}


class VoteRequestDTO(BaseModel):
    is_like: bool


@router.post('/{game_id}/comments/{comment_id}/vote')
async def vote_comment(
    game_id: int,
    comment_id: int,
    data: VoteRequestDTO,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    service = VoteCommentService.build(session)
    ok = await service.execute(
        game_id=game_id,
        comment_id=comment_id,
        user_id=current_user.id,
        is_like=data.is_like,
    )
    if ok is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Comment not found',
        )
    return {'ok': True}
