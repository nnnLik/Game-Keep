from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.games.game_comment_dao import GameCommentDAO
from daos.games.user_game_dao import UserGameDAO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class CreateCommentService:
    _comment_dao: GameCommentDAO
    _game_dao: UserGameDAO

    class CreateCommentServiceError(Exception):
        pass

    class GameNotFoundError(CreateCommentServiceError):
        pass

    class InvalidTextError(CreateCommentServiceError):
        pass

    class InvalidParentError(CreateCommentServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _comment_dao=GameCommentDAO.build(session),
            _game_dao=UserGameDAO.build(session),
        )

    async def execute(
        self,
        game_id: int,
        user_id: UUID,
        text: str,
        parent_id: int | None = None,
    ) -> int:
        game = await self._game_dao.get_by_id(game_id)
        if not game:
            raise self.GameNotFoundError

        text_stripped = text.strip()
        if not text_stripped or len(text_stripped) > 200:
            raise self.InvalidTextError

        if parent_id is not None:
            parent = await self._comment_dao.get_by_id(parent_id)
            if not parent or parent.game_id != game_id:
                raise self.InvalidParentError

        comment = await self._comment_dao.create(
            game_id=game_id,
            user_id=user_id,
            text=text_stripped,
            parent_id=parent_id,
        )
        return comment.id
