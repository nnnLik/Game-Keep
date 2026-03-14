from pydantic import BaseModel


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class LoginRequestDTO(BaseModel):
    username: str
    password: str


class RegisterRequestDTO(BaseModel):
    username: str
    password: str
