from uuid import UUID

from daos.games.game_comment_dao import GameCommentDAO
from sqlalchemy.ext.asyncio import AsyncSession


class VoteCommentService:
    def __init__(self, dao: GameCommentDAO) -> None:
        self._dao = dao

    @classmethod
    def build(cls, session: AsyncSession) -> 'VoteCommentService':
        return cls(dao=GameCommentDAO.build(session))

    async def execute(
        self,
        game_id: int,
        comment_id: int,
        user_id: UUID,
        is_like: bool,
    ) -> bool | None:
        comment = await self._dao.get_by_id(comment_id)
        if not comment or comment.game_id != game_id:
            return None

        existing = next(
            (v for v in await self._dao.get_user_votes(comment_id, user_id) if v.is_like == is_like),
            None,
        )
        if existing:
            await self._dao.remove_vote(comment_id, user_id, is_like)
        else:
            await self._dao.add_vote(comment_id, user_id, is_like)
        return True
