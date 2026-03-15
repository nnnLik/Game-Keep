from dataclasses import dataclass
from typing import Self

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    TITLE: str = 'App'
    VERSION: str = '0.1.0'
    HOST: str = Field('0.0.0.0', alias='HOST')
    PORT: int = Field(9999, alias='PORT')
    RELOAD: bool = Field(True, alias='RELOAD')
    LOG_LEVEL: str = Field('info', alias='LOG_LEVEL')
    UPLOADS_DIR: str = Field('uploads', alias='UPLOADS_DIR')


class DBSettings(BaseSettings):
    URL: str = Field('sqlite+aiosqlite:///./data.db', alias='DATABASE_URL')
    ECHO: bool = Field(False, alias='DB_ECHO')


class AuthSettings(BaseSettings):
    SECRET_KEY: str = Field('change-me', alias='SECRET_KEY')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, alias='REFRESH_TOKEN_EXPIRE_DAYS')
    ALGORITHM: str = Field('HS256', alias='JWT_ALGORITHM')


@dataclass
class Settings:
    app: AppSettings
    db: DBSettings
    auth: AuthSettings

    @classmethod
    def build(cls) -> Self:
        return cls(
            app=AppSettings(),
            db=DBSettings(),
            auth=AuthSettings(),
        )


settings = Settings.build()
