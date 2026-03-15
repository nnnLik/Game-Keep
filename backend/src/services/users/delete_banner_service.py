from dataclasses import dataclass
from pathlib import Path
from typing import Self
from uuid import UUID

from daos.auth.user_dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.static import get_banners_dir


@dataclass
class DeleteBannerService:
    _user_dao: UserDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    async def execute(self, user_id: UUID) -> None:
        banners_dir = Path(get_banners_dir())
        path = banners_dir / f'{user_id}.png'
        if path.exists():
            path.unlink()
        await self._user_dao.clear_banner(user_id)
