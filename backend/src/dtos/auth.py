from pydantic import BaseModel, EmailStr


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


class RegisterRequestDTO(BaseModel):
    username: str
    tag: str
    email: EmailStr
    password: str
