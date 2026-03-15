from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.activity import ActivityDAO
from dtos.feed import FeedPageResponseDTO
from services.feed.build_feed_post_dtos_service import BuildFeedPostDtosService
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GetUserActivityService:
    _activity_dao: ActivityDAO
    _build_dtos: BuildFeedPostDtosService

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _activity_dao=ActivityDAO.build(session),
            _build_dtos=BuildFeedPostDtosService.build(session),
        )

    async def execute(
        self,
        user_tag: str,
        current_user_id: UUID | None,
        cursor: int | None = None,
        limit: int = 20,
    ) -> FeedPageResponseDTO:
        activities, next_cursor = await self._activity_dao.get_activity_page_by_user_tag(
            user_tag=user_tag,
            limit=limit,
            cursor=cursor,
        )
        items = await self._build_dtos.execute(activities, current_user_id)
        return FeedPageResponseDTO(
            items=items,
            next_cursor=next_cursor,
            has_more=next_cursor is not None,
        )
