from dataclasses import dataclass
from typing import Any, Self


@dataclass
class SteamGameDetailDTO:
    type: str
    name: str
    steam_appid: int
    required_age: int
    is_free: bool
    controller_support: str
    dlc: list[int]
    detailed_description: str
    about_the_game: str
    short_description: str
    supported_languages: str
    reviews: str
    header_image: str | None
    capsule_image: str | None
    capsule_imagev5: str | None
    website: str | None
    pc_requirements: dict[str, Any]
    mac_requirements: dict[str, Any]
    linux_requirements: dict[str, Any]
    developers: list[str]
    publishers: list[str]
    price_overview: dict[str, Any] | None
    packages: list[int]
    package_groups: list[dict[str, Any]]
    platforms: dict[str, bool]
    metacritic: dict[str, Any] | None
    categories: list[dict[str, Any]]
    genres: list[dict[str, Any]]
    screenshots: list[dict[str, Any]]
    movies: list[dict[str, Any]]
    recommendations: dict[str, Any]
    achievements: dict[str, Any]
    release_date: dict[str, Any]
    support_info: dict[str, Any]
    background: str | None
    background_raw: str | None
    content_descriptors: dict[str, Any] | None
    ratings: dict[str, Any] | None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Self:
        return cls(
            type=d.get('type', ''),
            name=d.get('name', ''),
            steam_appid=d.get('steam_appid', 0),
            required_age=d.get('required_age', 0),
            is_free=d.get('is_free', False),
            controller_support=d.get('controller_support', ''),
            dlc=d.get('dlc') or [],
            detailed_description=d.get('detailed_description', ''),
            about_the_game=d.get('about_the_game', ''),
            short_description=d.get('short_description', ''),
            supported_languages=d.get('supported_languages', ''),
            reviews=d.get('reviews', ''),
            header_image=d.get('header_image'),
            capsule_image=d.get('capsule_image'),
            capsule_imagev5=d.get('capsule_imagev5'),
            website=d.get('website'),
            pc_requirements=d.get('pc_requirements') or {},
            mac_requirements=d.get('mac_requirements') or {},
            linux_requirements=d.get('linux_requirements') or {},
            developers=d.get('developers') or [],
            publishers=d.get('publishers') or [],
            price_overview=d.get('price_overview'),
            packages=d.get('packages') or [],
            package_groups=d.get('package_groups') or [],
            platforms=d.get('platforms') or {},
            metacritic=d.get('metacritic'),
            categories=d.get('categories') or [],
            genres=d.get('genres') or [],
            screenshots=d.get('screenshots') or [],
            movies=d.get('movies') or [],
            recommendations=d.get('recommendations') or {},
            achievements=d.get('achievements') or {},
            release_date=d.get('release_date') or {},
            support_info=d.get('support_info') or {},
            background=d.get('background'),
            background_raw=d.get('background_raw'),
            content_descriptors=d.get('content_descriptors'),
            ratings=d.get('ratings'),
        )


@dataclass
class SteamAppResponseDTO:
    success: bool
    data: SteamGameDetailDTO | None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Self:
        data_raw = d.get('data')
        data = SteamGameDetailDTO.from_dict(data_raw) if data_raw else None
        return cls(success=d.get('success', False), data=data)

    @classmethod
    def from_api_response(cls, raw: dict[str, Any], app_id: str) -> Self:
        return cls.from_dict(raw.get(app_id, {}))
