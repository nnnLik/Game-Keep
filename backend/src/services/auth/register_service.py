from dataclasses import dataclass
from typing import Self

from daos.auth.user_dao import UserDAO
from dtos.auth import RegisterRequestDTO, TokenResponseDTO
from services.auth.create_password_service import CreatePasswordService
from services.auth.create_token_service import CreateTokenService
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RegisterService:
    _user_dao: UserDAO
    _create_password: CreatePasswordService
    _create_token: CreateTokenService

    class RegisterServiceError(Exception):
        pass

    class UserAlreadyExistsError(RegisterServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_dao=UserDAO.build(session),
            _create_password=CreatePasswordService.build(),
            _create_token=CreateTokenService.build(),
        )

    async def execute(self, request: RegisterRequestDTO) -> TokenResponseDTO:
        existing = await self._user_dao.get_by_username(request.username)
        if existing:
            raise self.UserAlreadyExistsError
        password_hash = self._create_password.execute(request.password)
        user = await self._user_dao.create(request.username, password_hash)
        token = self._create_token.execute(user.id)
        return TokenResponseDTO(access_token=token)
