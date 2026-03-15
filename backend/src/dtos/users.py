from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MeResponseDTO(BaseModel):
    id: UUID
    username: str
    tag: str
    email: str
    created_at: datetime


class GameResponseDTO(BaseModel):
    id: int
    name: str
    state: str
    is_favorite: bool
