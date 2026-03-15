from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.games import (
    CommentResponseDTO,
    CreateCommentRequestDTO,
    GameDetailResponseDTO,
    VoteRequestDTO,
)
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.games import (
    CreateCommentService,
    GetCommentsService,
    GetGameService,
    VoteCommentService,
)

router = APIRouter(prefix="/games", tags=["games"])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/{game_id}", response_model=GameDetailResponseDTO)
async def get_game(game_id: int, session: SessionDep) -> GameDetailResponseDTO:
    service = GetGameService.build(session)
    result = await service.execute(game_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )
    return result


@router.get("/{game_id}/comments", response_model=list[CommentResponseDTO])
async def get_comments(
    game_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[CommentResponseDTO]:
    service = GetCommentsService.build(session)
    try:
        return await service.execute(game_id, current_user.id)
    except GetCommentsService.GameNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )


@router.post("/{game_id}/comments")
async def create_comment(
    game_id: int,
    data: CreateCommentRequestDTO,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> int:
    service = CreateCommentService.build(session)
    try:
        return await service.execute(
            game_id=game_id,
            user_id=current_user.id,
            text=data.text,
            parent_id=data.parent_id,
        )
    except CreateCommentService.GameNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )
    except CreateCommentService.InvalidTextError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid text (1-200 chars) or parent",
        )
    except CreateCommentService.InvalidParentError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent",
        )


@router.post("/{game_id}/comments/{comment_id}/vote")
async def vote_comment(
    game_id: int,
    comment_id: int,
    data: VoteRequestDTO,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> None:
    service = VoteCommentService.build(session)
    try:
        await service.execute(
            game_id=game_id,
            comment_id=comment_id,
            user_id=current_user.id,
            is_like=data.is_like,
        )
    except VoteCommentService.CommentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
