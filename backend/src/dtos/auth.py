import re

from pydantic import BaseModel, EmailStr, field_validator


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshRequestDTO(BaseModel):
    refresh_token: str


class LoginRequestDTO(BaseModel):
    email: EmailStr
    password: str


class RegisterStartRequestDTO(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class CompleteRegistrationRequestDTO(BaseModel):
    username: str
    tag: str

    @field_validator('username')
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError('Username must be at least 5 characters')
        return v

    @field_validator('tag')
    @classmethod
    def tag_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 3 or len(v) > 15:
            raise ValueError('Tag must be 3-15 characters')
        if not re.fullmatch(r'[a-z0-9]+', v):
            raise ValueError('Tag must contain only letters and digits')
        return v


class RegisterRequestDTO(BaseModel):
    username: str
    tag: str
    email: EmailStr
    password: str

    @field_validator('username')
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError('Username must be at least 5 characters')
        return v

    @field_validator('tag')
    @classmethod
    def tag_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 3 or len(v) > 15:
            raise ValueError('Tag must be 3-15 characters')
        if not re.fullmatch(r'[a-z0-9]+', v):
            raise ValueError('Tag must contain only letters and digits')
        return v

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
