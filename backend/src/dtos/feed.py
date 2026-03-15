from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from constants.activity import ActivityActionType
from dtos.games import CommentResponseDTO


class FeedPostAuthorDTO(BaseModel):
    username: str | None
    tag: str | None
    avatar_url: str | None


class FeedPostGameDTO(BaseModel):
    id: int
    name: str
    image_url: str | None
    state: str


class FeedPostCurrentUserVotedDTO(BaseModel):
    liked: bool
    disliked: bool


class FeedPostDTO(BaseModel):
    id: int
    action_type: ActivityActionType
    created_at: datetime
    author: FeedPostAuthorDTO
    game: FeedPostGameDTO
    like_count: int
    dislike_count: int
    current_user_voted: FeedPostCurrentUserVotedDTO
    comments: list[CommentResponseDTO] | None = None
    comments_total: int | None = None


class FeedPageResponseDTO(BaseModel):
    items: list[FeedPostDTO]
    next_cursor: int | None
    has_more: bool
