from dataclasses import dataclass
from uuid import UUID
from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from constants.activity import ActivityActionType
from models.activity import Activity
from models.user import User


@dataclass
class ActivityDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_session=session)

    async def create(
        self,
        user_id: UUID,
        action_type: ActivityActionType,
        user_game_id: int,
    ) -> Activity:
        activity = Activity(
            user_id=user_id,
            action_type=action_type,
            user_game_id=user_game_id,
        )
        self._session.add(activity)
        await self._session.flush()
        await self._session.refresh(activity)
        return activity

    async def get_feed_page(
        self,
        limit: int = 20,
        cursor: int | None = None,
    ) -> tuple[list[Activity], int | None]:
        stmt = (
            select(Activity)
            .options(
                selectinload(Activity.user),
                selectinload(Activity.user_game),
                selectinload(Activity.votes),
            )
            .order_by(Activity.created_at.desc(), Activity.id.desc())
            .limit(limit + 1)
        )
        if cursor is not None:
            stmt = stmt.where(Activity.id < cursor)
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]
            next_cursor = rows[-1].id
        else:
            next_cursor = None
        return rows, next_cursor

    async def get_activity_page_by_user_tag(
        self,
        user_tag: str,
        limit: int = 20,
        cursor: int | None = None,
    ) -> tuple[list[Activity], int | None]:
        stmt = (
            select(Activity)
            .join(User, Activity.user_id == User.id)
            .where(User.tag == user_tag)
            .options(
                selectinload(Activity.user),
                selectinload(Activity.user_game),
                selectinload(Activity.votes),
            )
            .order_by(Activity.created_at.desc(), Activity.id.desc())
            .limit(limit + 1)
        )
        if cursor is not None:
            stmt = stmt.where(Activity.id < cursor)
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]
            next_cursor = rows[-1].id
        else:
            next_cursor = None
        return rows, next_cursor
