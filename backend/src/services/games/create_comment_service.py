from uuid import UUID

from daos.games.game_comment_dao import GameCommentDAO
from daos.games.user_game_dao import UserGameDAO
from sqlalchemy.ext.asyncio import AsyncSession


class CreateCommentService:
    def __init__(
        self,
        comment_dao: GameCommentDAO,
        game_dao: UserGameDAO,
    ) -> None:
        self._comment_dao = comment_dao
        self._game_dao = game_dao

    @classmethod
    def build(cls, session: AsyncSession) -> 'CreateCommentService':
        return cls(
            comment_dao=GameCommentDAO.build(session),
            game_dao=UserGameDAO.build(session),
        )

    async def execute(
        self,
        game_id: int,
        user_id: UUID,
        text: str,
        parent_id: int | None = None,
    ) -> tuple[int | None, str | None]:
        """Returns (comment_id, error). error is 'not_found' or 'bad_request' or None."""
        game = await self._game_dao.get_by_id(game_id)
        if not game:
            return (None, 'not_found')

        text_stripped = text.strip()
        if not text_stripped or len(text_stripped) > 200:
            return (None, 'bad_request')

        if parent_id is not None:
            parent = await self._comment_dao.get_by_id(parent_id)
            if not parent or parent.game_id != game_id:
                return (None, 'bad_request')

        comment = await self._comment_dao.create(
            game_id=game_id,
            user_id=user_id,
            text=text_stripped,
            parent_id=parent_id,
        )
        return (comment.id, None)
