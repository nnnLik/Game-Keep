import re
from dataclasses import dataclass
from typing import ClassVar, Self

import httpx

from dtos.games import GenreDTO
from dtos.steam_api import SteamAppResponseDTO


@dataclass
class FetchSteamGameResult:
    name: str
    image_url: str | None
    steam_app_id: str
    genres: list[GenreDTO]
    developers: list[str]
    publishers: list[str]


class FetchSteamGameService:
    STEAM_API_URL: ClassVar[str] = 'https://store.steampowered.com/api/appdetails'
    STEAM_APP_URL_PATTERN: ClassVar[re.Pattern] = re.compile(
        r'https?://store\.steampowered\.com/app/(\d+)',
        re.IGNORECASE,
    )
    TIMEOUT: ClassVar[int] = 10

    class FetchSteamGameError(Exception):
        pass

    class InvalidSteamUrlError(FetchSteamGameError):
        pass

    class GameNotFoundError(FetchSteamGameError):
        pass

    @classmethod
    def build(cls) -> Self:
        return cls()

    def _extract_app_id(self, steam_url: str) -> str | None:
        match = self.STEAM_APP_URL_PATTERN.search(steam_url.strip())
        return match.group(1) if match else None

    def execute(self, steam_url: str) -> FetchSteamGameResult:
        app_id = self._extract_app_id(steam_url)
        if not app_id:
            raise self.InvalidSteamUrlError('Invalid Steam URL')

        with httpx.Client(timeout=self.TIMEOUT) as client:
            resp = client.get(
                self.STEAM_API_URL,
                params={'appids': app_id, 'l': 'english'},
            )
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise self.GameNotFoundError('Game not found on Steam') from e

        steam_response_dto = SteamAppResponseDTO.from_api_response(resp.json(), app_id)
        if not steam_response_dto.success or not steam_response_dto.data:
            raise self.GameNotFoundError('Game not found on Steam')

        game_detail_dto = steam_response_dto.data
        genres = [
            GenreDTO(id=str(g.get('id', '')), description=str(g.get('description', '')))
            for g in (game_detail_dto.genres or [])
            if isinstance(g, dict)
        ]
        developers = list(game_detail_dto.developers or [])
        publishers = list(game_detail_dto.publishers or [])

        return FetchSteamGameResult(
            name=game_detail_dto.name,
            image_url=game_detail_dto.header_image,
            steam_app_id=app_id,
            genres=genres,
            developers=developers,
            publishers=publishers,
        )
