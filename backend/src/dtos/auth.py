from pydantic import BaseModel


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshRequestDTO(BaseModel):
    refresh_token: str


class LoginRequestDTO(BaseModel):
    username: str
    password: str


class RegisterRequestDTO(BaseModel):
    username: str
    password: str
