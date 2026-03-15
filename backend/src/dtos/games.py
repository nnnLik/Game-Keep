from pydantic import BaseModel


class FetchSteamResponseDTO(BaseModel):
    name: str
    image_url: str | None
    steam_app_id: str
