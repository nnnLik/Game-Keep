from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

import constants.game


class CreateGameRequestDTO(BaseModel):
    name: str
    state: str
    is_favorite: bool = False

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


class MeResponseDTO(BaseModel):
    id: UUID
    username: str
    tag: str
    email: str
    created_at: datetime


class GameResponseDTO(BaseModel):
    id: int
    name: str
    state: constants.game.GameStateEnum
    is_favorite: bool
