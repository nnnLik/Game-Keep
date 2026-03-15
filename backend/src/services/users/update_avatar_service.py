from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Self
from uuid import UUID

from fastapi import UploadFile

from daos.auth.user_dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.static import get_avatars_dir


@dataclass
class UpdateAvatarService:
    _user_dao: UserDAO

    ALLOWED_EXTENSIONS: ClassVar[frozenset[str]] = frozenset(
        {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    )
    MAX_SIZE: ClassVar[int] = 25 * 1024 * 1024  # 25 MB

    class AvatarInvalidFormatError(Exception):
        pass

    class AvatarTooLargeError(Exception):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    async def execute(self, user_id: UUID, avatar: UploadFile) -> str:
        if not avatar or not avatar.filename:
            raise self.AvatarInvalidFormatError
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
        await self._user_dao.update_avatar(user_id, avatar_url)
        return avatar_url
