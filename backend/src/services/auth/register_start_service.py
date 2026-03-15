from dataclasses import dataclass
from typing import Self

from daos.auth.user_dao import UserDAO
from dtos.auth import TokenResponseDTO
from services.auth.create_password_service import CreatePasswordService
from services.auth.create_token_service import CreateTokenService
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RegisterStartService:
    _user_dao: UserDAO
    _create_password: CreatePasswordService
    _create_token: CreateTokenService

    class RegisterStartServiceError(Exception):
        pass

    class EmailAlreadyTakenError(RegisterStartServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_dao=UserDAO.build(session),
            _create_password=CreatePasswordService.build(),
            _create_token=CreateTokenService.build(),
        )

    async def execute(self, email: str, password: str) -> TokenResponseDTO:
        existing = await self._user_dao.get_by_email(email)
        if existing:
            raise self.EmailAlreadyTakenError

        password_hash = self._create_password.execute(password)
        user = await self._user_dao.create_minimal(email, password_hash)
        access_token, refresh_token = self._create_token.execute(user.id)
        return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)
