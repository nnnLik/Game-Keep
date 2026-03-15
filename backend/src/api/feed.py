from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.feed import FeedPageResponseDTO
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.feed import GetFeedService

router = APIRouter(prefix="/feed", tags=["feed"])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=FeedPageResponseDTO)
async def get_feed(
    current_user: CurrentUserDep,
    session: SessionDep,
    cursor: int | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
) -> FeedPageResponseDTO:
    service = GetFeedService.build(session)
    return await service.execute(
        current_user_id=current_user.id,
        cursor=cursor,
        limit=limit,
    )
