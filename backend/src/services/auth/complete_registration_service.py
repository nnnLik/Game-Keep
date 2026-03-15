import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Self
from uuid import UUID

from fastapi import UploadFile

from utils.static import get_avatars_dir
from daos.auth.user_dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class CompleteRegistrationService:
    _user_dao: UserDAO

    class CompleteRegistrationServiceError(Exception):
        pass

    class UsernameTooShortError(CompleteRegistrationServiceError):
        pass

    class TagTooShortError(CompleteRegistrationServiceError):
        pass

    class TagTooLongError(CompleteRegistrationServiceError):
        pass

    class TagInvalidCharactersError(CompleteRegistrationServiceError):
        pass

    class TagAlreadyTakenError(CompleteRegistrationServiceError):
        pass

    class UserNotFoundError(CompleteRegistrationServiceError):
        pass

    class UserAlreadyCompleteError(CompleteRegistrationServiceError):
        pass

    class AvatarInvalidFormatError(CompleteRegistrationServiceError):
        pass

    class AvatarTooLargeError(CompleteRegistrationServiceError):
        pass

    ALLOWED_EXTENSIONS: ClassVar[frozenset[str]] = frozenset({'jpg', 'jpeg', 'png', 'gif', 'webp'})
    MAX_SIZE: ClassVar[int] = 25 * 1024 * 1024 # 25 MB

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

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

    async def execute(
        self,
        user_id: UUID,
        username: str,
        tag: str,
        avatar: UploadFile | None = None,
    ) -> None:
        self._validate_username(username)
        tag = self._validate_tag(tag)

        user = await self._user_dao.get_by_id(user_id)
        if not user:
            raise self.UserNotFoundError
        if user.is_registration_complete:
            raise self.UserAlreadyCompleteError

        existing_tag = await self._user_dao.get_by_tag(tag)
        if existing_tag and existing_tag.id != user_id:
            raise self.TagAlreadyTakenError

        avatar_url: str | None = None
        if avatar and avatar.filename:
            ext = Path(avatar.filename).suffix.lower().lstrip('.')
            if ext not in self.ALLOWED_EXTENSIONS:
                raise self.AvatarInvalidFormatError
            content = await avatar.read()
            if len(content) > self.MAX_SIZE:
                raise self.AvatarTooLargeError
            avatars_dir = Path(get_avatars_dir())
            filename = f'{user_id}.{ext}'
            (avatars_dir / filename).write_bytes(content)
            avatar_url = f'avatars/{filename}'

        await self._user_dao.update_profile(user_id, username, tag, avatar_url)
