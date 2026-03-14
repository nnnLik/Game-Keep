from dataclasses import dataclass
from typing import Self
from uuid import UUID

import jwt

from conf.settings import settings
from dtos.auth import TokenResponseDTO
from services.auth.create_token_service import CreateTokenService


@dataclass
class RefreshTokenService:
    _create_token: CreateTokenService

    class RefreshTokenServiceError(Exception):
        pass

    class InvalidRefreshTokenError(RefreshTokenServiceError):
        pass

    @classmethod
    def build(cls) -> Self:
        return cls(_create_token=CreateTokenService.build())

    def execute(self, refresh_token: str) -> TokenResponseDTO:
        try:
            payload = jwt.decode(
                refresh_token,
                settings.auth.SECRET_KEY,
                algorithms=[settings.auth.ALGORITHM],
            )
            if payload.get('type') != 'refresh':
                raise self.InvalidRefreshTokenError
            user_id = UUID(payload['sub'])
        except (jwt.InvalidTokenError, KeyError, ValueError):
            raise self.InvalidRefreshTokenError

        access_token, new_refresh_token = self._create_token.execute(user_id)
        return TokenResponseDTO(access_token=access_token, refresh_token=new_refresh_token)
