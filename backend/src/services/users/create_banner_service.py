from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Self
from uuid import UUID

from fastapi import UploadFile

from daos.auth.user_dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.static import get_banners_dir


@dataclass
class CreateBannerService:
    _user_dao: UserDAO

    MAX_SIZE: ClassVar[int] = 2 * 1024 * 1024  # 2 MB

    class BannerTooLargeError(Exception):
        pass

    class InvalidFormatError(Exception):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    async def execute(self, user_id: UUID, file: UploadFile) -> str:
        if not file.filename or not file.filename.lower().endswith('.png'):
            raise self.InvalidFormatError
        content = await file.read()
        if len(content) > self.MAX_SIZE:
            raise self.BannerTooLargeError
        banners_dir = Path(get_banners_dir())
        filename = f'{user_id}.png'
        (banners_dir / filename).write_bytes(content)
        banner_url = f'banners/{filename}'
        await self._user_dao.update_banner(user_id, banner_url)
        return banner_url
