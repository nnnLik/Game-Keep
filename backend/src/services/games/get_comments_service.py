from datetime import datetime

from dataclasses import dataclass
from typing import ClassVar, Self
from uuid import UUID

from daos.games.game_comment_dao import GameCommentDAO
from daos.games.user_game_dao import UserGameDAO
from dtos.games import CommentAuthorDTO, CommentResponseDTO
from models.game_comment import GameComment
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GetCommentsService:
    _game_comment_dao: GameCommentDAO
    _user_game_dao: UserGameDAO

    MAX_DEPTH: ClassVar[int] = 5

    class GetCommentsServiceError(Exception):
        pass

    class GameNotFoundError(GetCommentsServiceError):
        pass

    @classmethod
    def build(
        cls,
        session: AsyncSession,
    ) -> Self:
        return cls(
            _game_comment_dao=GameCommentDAO.build(session),
            _user_game_dao=UserGameDAO.build(session),
        )

    def _to_dto(
        self,
        comment: GameComment,
        child_dtos: list[CommentResponseDTO],
        current_user_id: UUID | None,
    ) -> CommentResponseDTO:
        like_count = sum(1 for v in comment.votes if v.is_like)
        dislike_count = sum(1 for v in comment.votes if not v.is_like)
        liked = False
        disliked = False
        if current_user_id:
            for v in comment.votes:
                if v.user_id == current_user_id:
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

    def _build_tree(
        self,
        by_parent: dict[int | None, list[GameComment]],
        parent_id: int | None,
        depth: int,
        current_user_id: UUID | None,
    ) -> list[CommentResponseDTO]:
        if depth >= self.MAX_DEPTH:
            return []
        result = []
        for c in sorted(
            by_parent.get(parent_id, []),
            key=lambda x: x.created_at or datetime.min,
        ):
            child_dtos = self._build_tree(by_parent, c.id, depth + 1, current_user_id)
            result.append(self._to_dto(c, child_dtos, current_user_id))
        return result

    async def execute(self, game_id: int, current_user_id: UUID | None) -> list[CommentResponseDTO]:
        game = await self._user_game_dao.get_by_id(game_id)
        if not game:
            raise self.GameNotFoundError

        comments = await self._game_comment_dao.get_all_by_game_id(game_id)
        by_parent: dict[int | None, list[GameComment]] = {}
        for c in comments:
            pid = c.parent_id
            if pid not in by_parent:
                by_parent[pid] = []
            by_parent[pid].append(c)

        return self._build_tree(by_parent, None, 0, current_user_id)
