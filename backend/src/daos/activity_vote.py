from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.activity import Activity
from models.activity_vote import ActivityVote


@dataclass
class ActivityVoteDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> "ActivityVoteDAO":
        return cls(_session=session)

    async def get_activity_by_id(self, activity_id: int) -> Activity | None:
        stmt = select(Activity).where(Activity.id == activity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_votes(
        self,
        activity_id: int,
        user_id: UUID,
    ) -> list[ActivityVote]:
        stmt = select(ActivityVote).where(
            ActivityVote.activity_id == activity_id,
            ActivityVote.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_vote(
        self,
        activity_id: int,
        user_id: UUID,
        is_like: bool,
    ) -> ActivityVote:
        vote = ActivityVote(
            activity_id=activity_id,
            user_id=user_id,
            is_like=is_like,
        )
        self._session.add(vote)
        await self._session.flush()
        return vote

    async def remove_vote(
        self,
        activity_id: int,
        user_id: UUID,
        is_like: bool,
    ) -> bool:
        stmt = select(ActivityVote).where(
            ActivityVote.activity_id == activity_id,
            ActivityVote.user_id == user_id,
            ActivityVote.is_like == is_like,
        )
        result = await self._session.execute(stmt)
        vote = result.scalar_one_or_none()
        if vote:
            await self._session.delete(vote)
            await self._session.flush()
            return True
        return False
