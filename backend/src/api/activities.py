from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.games import VoteRequestDTO
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.feed.vote_activity_service import VoteActivityService

router = APIRouter(prefix="/activities", tags=["activities"])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("/{activity_id}/vote")
async def vote_activity(
    activity_id: int,
    data: VoteRequestDTO,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    service = VoteActivityService.build(session)
    try:
        await service.execute(activity_id, current_user.id, data.is_like)
    except VoteActivityService.ActivityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
