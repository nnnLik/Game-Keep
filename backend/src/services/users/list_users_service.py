import base64
import json
from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.auth.user_dao import UserDAO
from dtos.users import UserListItemDTO, UsersListResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ListUsersService:
    _user_dao: UserDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    def _encode_cursor(self, games_count: int, user_id: UUID) -> str:
        payload = {"g": games_count, "u": str(user_id)}
        return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    def _decode_cursor(self, cursor: str) -> tuple[int, UUID] | None:
        try:
            raw = base64.urlsafe_b64decode(cursor.encode())
            data = json.loads(raw.decode())
            return (data["g"], UUID(data["u"]))
        except Exception:
            return None

    async def execute(
        self,
        limit: int = 20,
        cursor: str | None = None,
    ) -> UsersListResponseDTO:
        limit = max(1, min(100, limit))
        cursor_games_count, cursor_user_id = (None, None)
        if cursor:
            decoded = self._decode_cursor(cursor)
            if decoded:
                cursor_games_count, cursor_user_id = decoded

        rows = await self._user_dao.get_list_with_games_count(
            limit=limit + 1,
            cursor_games_count=cursor_games_count,
            cursor_user_id=cursor_user_id,
        )

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        items = [
            UserListItemDTO(
                tag=u.tag,
                username=u.username,
                avatar_url=u.avatar_url,
                games_count=int(gc),
            )
            for u, gc in rows
        ]

        next_cursor = None
        if has_more and rows:
            last_user, last_gc = rows[-1]
            next_cursor = self._encode_cursor(int(last_gc), last_user.id)

        return UsersListResponseDTO(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
        )
