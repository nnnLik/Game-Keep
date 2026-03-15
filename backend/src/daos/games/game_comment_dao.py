from dataclasses import dataclass
from typing import Self
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.game_comment import GameComment
from models.game_comment_vote import GameCommentVote


@dataclass
class GameCommentDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_session=session)

    async def get_all_by_game_id(self, game_id: int) -> list[GameComment]:
        stmt = (
            select(GameComment)
            .options(
                selectinload(GameComment.user),
                selectinload(GameComment.votes),
            )
            .where(GameComment.game_id == game_id)
            .order_by(GameComment.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, comment_id: int) -> GameComment | None:
        stmt = (
            select(GameComment)
            .options(
                selectinload(GameComment.user),
                selectinload(GameComment.votes),
                selectinload(GameComment.children),
            )
            .where(GameComment.id == comment_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        game_id: int,
        user_id: UUID,
        text: str,
        parent_id: int | None = None,
    ) -> GameComment:
        comment = GameComment(
            game_id=game_id,
            user_id=user_id,
            text=text,
            parent_id=parent_id,
        )
        self._session.add(comment)
        await self._session.flush()
        await self._session.refresh(comment)
        return comment

    async def add_vote(self, comment_id: int, user_id: UUID, is_like: bool) -> GameCommentVote:
        vote = GameCommentVote(
            comment_id=comment_id,
            user_id=user_id,
            is_like=is_like,
        )
        self._session.add(vote)
        await self._session.flush()
        return vote

    async def remove_vote(self, comment_id: int, user_id: UUID, is_like: bool) -> bool:
        stmt = select(GameCommentVote).where(
            GameCommentVote.comment_id == comment_id,
            GameCommentVote.user_id == user_id,
            GameCommentVote.is_like == is_like,
        )
        result = await self._session.execute(stmt)
        vote = result.scalar_one_or_none()
        if vote:
            await self._session.delete(vote)
            await self._session.flush()
            return True
        return False

    async def get_user_votes(
        self,
        comment_id: int,
        user_id: UUID,
    ) -> list[GameCommentVote]:
        stmt = select(GameCommentVote).where(
            GameCommentVote.comment_id == comment_id,
            GameCommentVote.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
