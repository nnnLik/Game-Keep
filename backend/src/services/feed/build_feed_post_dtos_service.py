from dataclasses import dataclass
from typing import Self
from uuid import UUID

from constants.activity import ActivityActionType
from daos.games.game_comment_dao import GameCommentDAO
from dtos.feed import (
    FeedPostAuthorDTO,
    FeedPostCurrentUserVotedDTO,
    FeedPostDTO,
    FeedPostGameDTO,
)
from dtos.games import CommentResponseDTO
from models.activity import Activity
from services.games.get_comments_service import GetCommentsService
from sqlalchemy.ext.asyncio import AsyncSession

FEED_COMMENTS_PREVIEW = 3


@dataclass
class BuildFeedPostDtosService:
    _session: AsyncSession
    _game_comment_dao: GameCommentDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _session=session,
            _game_comment_dao=GameCommentDAO.build(session),
        )

    def _activity_to_dto(
        self,
        activity: Activity,
        current_user_id: UUID | None,
        comments: list[CommentResponseDTO] | None = None,
        comments_total: int | None = None,
    ) -> FeedPostDTO:
        like_count = sum(1 for v in activity.votes if v.is_like)
        dislike_count = sum(1 for v in activity.votes if not v.is_like)
        liked = False
        disliked = False
        if current_user_id:
            for v in activity.votes:
                if v.user_id == current_user_id:
                    if v.is_like:
                        liked = True
                    else:
                        disliked = True

        user = activity.user
        author = FeedPostAuthorDTO(
            username=user.username,
            tag=user.tag,
            avatar_url=user.avatar_url,
        )

        game = activity.user_game
        game_dto = FeedPostGameDTO(
            id=game.id,
            name=game.name,
            image_url=game.image_url,
            state=str(game.state),
        )

        return FeedPostDTO(
            id=activity.id,
            action_type=activity.action_type,
            created_at=activity.created_at,
            author=author,
            game=game_dto,
            like_count=like_count,
            dislike_count=dislike_count,
            current_user_voted=FeedPostCurrentUserVotedDTO(liked=liked, disliked=disliked),
            comments=comments,
            comments_total=comments_total,
        )

    async def execute(
        self,
        activities: list[Activity],
        current_user_id: UUID | None,
    ) -> list[FeedPostDTO]:
        get_comments = GetCommentsService.build(self._session)
        result = []
        for activity in activities:
            comments: list[CommentResponseDTO] | None = None
            comments_total: int | None = None
            if activity.action_type == ActivityActionType.GAME_CREATED:
                try:
                    all_comments = await get_comments.execute(
                        activity.user_game_id,
                        current_user_id,
                    )
                    comments = all_comments[:FEED_COMMENTS_PREVIEW]
                    comments_total = await self._game_comment_dao.get_root_comments_count(
                        activity.user_game_id
                    )
                except GetCommentsService.GameNotFoundError:
                    pass

            result.append(
                self._activity_to_dto(
                    activity,
                    current_user_id,
                    comments=comments,
                    comments_total=comments_total,
                )
            )
        return result
