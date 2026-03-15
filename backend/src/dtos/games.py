from datetime import date

from pydantic import BaseModel

import constants.game


class GameOwnerDTO(BaseModel):
    username: str | None
    tag: str | None
    avatar_url: str | None


class GameDetailResponseDTO(BaseModel):
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
    view_count: int
    owner: GameOwnerDTO


class GenreDTO(BaseModel):
    id: str
    description: str


class FetchSteamResponseDTO(BaseModel):
    name: str
    image_url: str | None
    steam_app_id: str
    genres: list[GenreDTO] = []
    developers: list[str] = []
    publishers: list[str] = []
    release_date: str | None = None
