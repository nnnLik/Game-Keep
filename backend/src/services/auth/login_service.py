from dataclasses import dataclass
from typing import Self

from daos.auth.user_dao import UserDAO
from dtos.auth import TokenResponseDTO
from services.auth.create_token_service import CreateTokenService
from services.auth.verify_password_service import VerifyPasswordService
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class LoginService:
    _user_dao: UserDAO
    _verify_password: VerifyPasswordService
    _create_token: CreateTokenService

    class LoginServiceError(Exception):
        pass

    class InvalidCredentialsError(LoginServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_dao=UserDAO.build(session),
            _verify_password=VerifyPasswordService.build(),
            _create_token=CreateTokenService.build(),
        )

    async def execute(self, email: str, password: str) -> TokenResponseDTO:
        user = await self._user_dao.get_by_email(email)
        if not user or not self._verify_password.execute(password, user.password):
            raise self.InvalidCredentialsError
        access_token, refresh_token = self._create_token.execute(user.id)
        return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)
