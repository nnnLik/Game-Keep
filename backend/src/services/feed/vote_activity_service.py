from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.activity_vote import ActivityVoteDAO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class VoteActivityService:
    _activity_vote_dao: ActivityVoteDAO

    class VoteActivityServiceError(Exception):
        pass

    class ActivityNotFoundError(VoteActivityServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_activity_vote_dao=ActivityVoteDAO.build(session))

    async def execute(
        self,
        activity_id: int,
        user_id: UUID,
        is_like: bool,
    ) -> None:
        activity = await self._activity_vote_dao.get_activity_by_id(activity_id)
        if not activity:
            raise self.ActivityNotFoundError

        existing = next(
            (
                v
                for v in await self._activity_vote_dao.get_user_votes(activity_id, user_id)
                if v.is_like == is_like
            ),
            None,
        )
        if existing:
            await self._activity_vote_dao.remove_vote(activity_id, user_id, is_like)
        else:
            await self._activity_vote_dao.add_vote(activity_id, user_id, is_like)
