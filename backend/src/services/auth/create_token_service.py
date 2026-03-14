from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Self
from uuid import UUID

import jwt

from conf.settings import settings


@dataclass
class CreateTokenService:
    @classmethod
    def build(cls) -> Self:
        return cls()

    def execute(self, user_id: UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {'sub': str(user_id), 'exp': expire}
        return jwt.encode(payload, settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM)
