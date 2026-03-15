from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.auth.user_dao import UserDAO
from dtos.users import MeResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class MeService:
    _user_dao: UserDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    async def execute(self, user_id: UUID) -> MeResponseDTO:
        user = await self._user_dao.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        return MeResponseDTO(
            id=user.id,
            username=user.username,
            tag=user.tag,
            email=user.email,
            created_at=user.created_at,
        )
