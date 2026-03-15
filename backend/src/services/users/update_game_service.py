from dataclasses import dataclass
from datetime import date
from typing import Self
from uuid import UUID

import constants.game
from constants.activity import ActivityActionType
from daos.activity import ActivityDAO
from daos.games.user_game_dao import UserGameDAO
from dtos.users import GameResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class UpdateGameService:
    _user_game_dao: UserGameDAO
    _activity_dao: ActivityDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_game_dao=UserGameDAO.build(session),
            _activity_dao=ActivityDAO.build(session),
        )

    def _genres_to_response(
        self,
        genres: list[str] | list[dict[str, str]] | None,
    ) -> list[dict[str, str]] | None:
        if not genres:
            return None
        strings = [s if isinstance(s, str) else s.get('description', '') for s in genres]
        result = [{'id': str(i), 'description': s} for i, s in enumerate(strings) if s]
        return result or None

    async def execute(
        self,
        game_id: int,
        user_id: UUID,
        **data: object,
    ) -> GameResponseDTO | None:
        kwargs: dict[str, object] = {}
        if 'name' in data:
            kwargs['name'] = data['name']
        if 'state' in data:
            kwargs['state'] = constants.game.GameStateEnum(data['state'])
        if 'is_favorite' in data:
            kwargs['is_favorite'] = data['is_favorite']
        if 'image_url' in data:
            kwargs['image_url'] = data['image_url']
        if 'steam_app_id' in data:
            kwargs['steam_app_id'] = data['steam_app_id']
        if 'genres' in data:
            genres_raw = data['genres'] or []
            kwargs['genres'] = list(
                dict.fromkeys(
                    (g.get('description', '') if isinstance(g, dict) else '')
                    for g in genres_raw
                    if isinstance(g, dict) and g.get('description')
                )
            )
        if 'developers' in data:
            kwargs['developers'] = list(dict.fromkeys(data['developers'] or []))
        if 'publishers' in data:
            kwargs['publishers'] = list(dict.fromkeys(data['publishers'] or []))
        if 'release_date' in data:
            kwargs['release_date'] = data['release_date']
        if 'note' in data:
            kwargs['note'] = data['note']
        if 'date_started' in data:
            kwargs['date_started'] = data['date_started']
        if 'date_finished' in data:
            kwargs['date_finished'] = data['date_finished']
        if 'hours_played' in data:
            h = data['hours_played']
            kwargs['hours_played'] = round(h, 1) if h is not None else None

        if 'is_favorite' in kwargs:
            old_game = await self._user_game_dao.get_by_id(game_id)
            if (
                old_game
                and old_game.user_id == user_id
                and old_game.is_favorite != kwargs['is_favorite']
            ):
                action = (
                    ActivityActionType.FAVORITE_ADDED
                    if kwargs['is_favorite']
                    else ActivityActionType.FAVORITE_REMOVED
                )
                await self._activity_dao.create(
                    user_id=user_id,
                    action_type=action,
                    user_game_id=game_id,
                )

        game = await self._user_game_dao.update(game_id, user_id, **kwargs)
        if game is None:
            return None
        return GameResponseDTO(
            id=game.id,
            name=game.name,
            image_url=game.image_url,
            steam_app_id=game.steam_app_id,
            state=game.state,
            is_favorite=game.is_favorite,
            genres=self._genres_to_response(game.genres),
            developers=game.developers,
            publishers=game.publishers,
            release_date=game.release_date,
            note=game.note,
            date_started=game.date_started,
            date_finished=game.date_finished,
            hours_played=game.hours_played,
        )
