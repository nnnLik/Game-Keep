import re
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

    class UsernameTooShortError(RegisterServiceError):
        pass

    class TagTooShortError(RegisterServiceError):
        pass

    class TagTooLongError(RegisterServiceError):
        pass

    class TagInvalidCharactersError(RegisterServiceError):
        pass

    class TagAlreadyTakenError(RegisterServiceError):
        pass

    class EmailAlreadyTakenError(RegisterServiceError):
        pass

    class PasswordTooShortError(RegisterServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_dao=UserDAO.build(session),
            _create_password=CreatePasswordService.build(),
            _create_token=CreateTokenService.build(),
        )

    def _validate_username(self, username: str) -> None:
        if len(username) < 5:
            raise self.UsernameTooShortError

    def _validate_tag(self, tag: str) -> str:
        tag = tag.strip().lower()
        if len(tag) < 3:
            raise self.TagTooShortError
        if len(tag) > 15:
            raise self.TagTooLongError
        if not re.fullmatch(r'[a-z0-9]+', tag):
            raise self.TagInvalidCharactersError
        return tag

    def _validate_password(self, password: str) -> None:
        if len(password) < 8:
            raise self.PasswordTooShortError

    async def execute(
        self,
        username: str,
        tag: str,
        email: str,
        password: str,
    ) -> TokenResponseDTO:
        self._validate_username(username)
        tag = self._validate_tag(tag)
        self._validate_password(password)

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
