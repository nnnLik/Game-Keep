from dataclasses import dataclass
from typing import Self

from daos.auth.user_dao import UserDAO
from dtos.auth import TokenResponseDTO
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

    class TagAlreadyTakenError(RegisterServiceError):
        pass

    class EmailAlreadyTakenError(RegisterServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_dao=UserDAO.build(session),
            _create_password=CreatePasswordService.build(),
            _create_token=CreateTokenService.build(),
        )

    async def execute(
        self,
        username: str,
        tag: str,
        email: str,
        password: str,
    ) -> TokenResponseDTO:
        existing_tag = await self._user_dao.get_by_tag(tag)
        if existing_tag:
            raise self.TagAlreadyTakenError

        existing_email = await self._user_dao.get_by_email(email)
        if existing_email:
            raise self.EmailAlreadyTakenError

        password_hash = self._create_password.execute(password)
        user = await self._user_dao.create(username, tag, email, password_hash)
        access_token, refresh_token = self._create_token.execute(user.id)
        return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)
