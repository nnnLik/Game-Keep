from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.games.game_comment_dao import GameCommentDAO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class VoteCommentService:
    _comment_dao: GameCommentDAO

    class VoteCommentServiceError(Exception):
        pass

    class CommentNotFoundError(VoteCommentServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_comment_dao=GameCommentDAO.build(session))

    async def execute(
        self,
        game_id: int,
        comment_id: int,
        user_id: UUID,
        is_like: bool,
    ) -> None:
        comment = await self._comment_dao.get_by_id(comment_id)
        if not comment or comment.game_id != game_id:
            raise self.CommentNotFoundError

        existing = next(
            (v for v in await self._comment_dao.get_user_votes(comment_id, user_id) if v.is_like == is_like),
            None,
        )
        if existing:
            await self._comment_dao.remove_vote(comment_id, user_id, is_like)
        else:
            await self._comment_dao.add_vote(comment_id, user_id, is_like)
