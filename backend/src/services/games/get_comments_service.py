from datetime import datetime
from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.games.game_comment_dao import GameCommentDAO
from dtos.games import CommentAuthorDTO, CommentResponseDTO
from models.game_comment import GameComment
from sqlalchemy.ext.asyncio import AsyncSession

MAX_DEPTH = 5


@dataclass
class GetCommentsService:
    _game_comment_dao: GameCommentDAO
    _current_user_id: UUID | None

    @classmethod
    def build(
        cls,
        session: AsyncSession,
        current_user_id: UUID | None = None,
    ) -> Self:
        return cls(
            _game_comment_dao=GameCommentDAO.build(session),
            current_user_id=current_user_id,
        )

    def _to_dto(
        self,
        comment: GameComment,
        child_dtos: list[CommentResponseDTO],
    ) -> CommentResponseDTO:
        like_count = sum(1 for v in comment.votes if v.is_like)
        dislike_count = sum(1 for v in comment.votes if not v.is_like)
        liked = False
        disliked = False
        if self._current_user_id:
            for v in comment.votes:
                if v.user_id == self._current_user_id:
                    if v.is_like:
                        liked = True
                    else:
                        disliked = True

        user = comment.user
        author = CommentAuthorDTO(
            username=user.username,
            tag=user.tag,
            avatar_url=user.avatar_url,
        )

        return CommentResponseDTO(
            id=comment.id,
            text=comment.text,
            created_at=comment.created_at,
            author=author,
            like_count=like_count,
            dislike_count=dislike_count,
            current_user_voted={'liked': liked, 'disliked': disliked},
            children=child_dtos,
        )

    async def execute(self, game_id: int) -> list[CommentResponseDTO]:
        comments = await self._game_comment_dao.get_all_by_game_id(game_id)
        by_parent: dict[int | None, list[GameComment]] = {}
        for c in comments:
            pid = c.parent_id
            if pid not in by_parent:
                by_parent[pid] = []
            by_parent[pid].append(c)

        def build_tree(parent_id: int | None, depth: int) -> list[CommentResponseDTO]:
            if depth >= MAX_DEPTH:
                return []
            result = []
            for c in sorted(
                by_parent.get(parent_id, []),
                key=lambda x: x.created_at or datetime.min,
            ):
                child_dtos = build_tree(c.id, depth + 1)
                result.append(self._to_dto(c, child_dtos))
            return result

        return build_tree(None, 0)
