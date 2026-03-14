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

    def execute(self, user_id: UUID) -> tuple[str, str]:
        now = datetime.now(timezone.utc)
        access_expire = now + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expire = now + timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS)

        access_payload = {'sub': str(user_id), 'exp': access_expire, 'type': 'access'}
        refresh_payload = {'sub': str(user_id), 'exp': refresh_expire, 'type': 'refresh'}

        access_token = jwt.encode(
            access_payload, settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM
        )
        refresh_token = jwt.encode(
            refresh_payload, settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM
        )
        return access_token, refresh_token
