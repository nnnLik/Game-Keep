from pydantic import BaseModel


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
