from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

import constants.game


class CreateGameRequestDTO(BaseModel):
    name: str
    image_url: str | None = None
    steam_app_id: str | None = None
    state: str
    is_favorite: bool = False
    genres: list[dict[str, str]] | None = None  # [{"id":"1","description":"Action"}]
    developers: list[str] | None = None
    publishers: list[str] | None = None
    release_date: str | None = None
    note: str | None = None
    date_started: date | None = None
    date_finished: date | None = None
    hours_played: float | None = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name is required')
        return v.strip()

    @field_validator('state')
    @classmethod
    def state_valid(cls, v: str) -> str:
        if v not in {e.value for e in constants.game.GameStateEnum}:
            raise ValueError('Invalid state')
        return v

    @field_validator('note')
    @classmethod
    def note_max_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError('Note max 500 characters')
        return v

    @field_validator('hours_played')
    @classmethod
    def hours_played_non_negative(cls, v: float | None) -> float | None:
        if v is None:
            return None
        if v != v or v < 0:  # NaN or negative
            raise ValueError('Hours played must be >= 0')
        return round(v, 1)


class MeResponseDTO(BaseModel):
    id: UUID
    username: str | None
    tag: str | None
    email: str
    created_at: datetime
    is_registration_complete: bool
    avatar_url: str | None
    banner_url: str | None


class GameResponseDTO(BaseModel):
    id: int
    name: str
    image_url: str | None
    steam_app_id: str | None
    state: constants.game.GameStateEnum
    is_favorite: bool
    genres: list[dict[str, str]] | None = None
    developers: list[str] | None = None
    publishers: list[str] | None = None
    release_date: str | None = None
    note: str | None = None
    date_started: date | None = None
    date_finished: date | None = None
    hours_played: float | None = None
