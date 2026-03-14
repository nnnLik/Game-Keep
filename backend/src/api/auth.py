from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.auth import LoginRequestDTO, RefreshRequestDTO, RegisterRequestDTO, TokenResponseDTO
from infra.db import get_db
from services.auth import LoginService, RefreshTokenService, RegisterService

router = APIRouter(prefix='/auth', tags=['auth'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post('/refresh', response_model=TokenResponseDTO)
async def refresh(data: RefreshRequestDTO) -> TokenResponseDTO:
    service = RefreshTokenService.build()
    try:
        return service.execute(data.refresh_token)
    except RefreshTokenService.InvalidRefreshTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        ) from e


@router.post('/login', response_model=TokenResponseDTO)
async def login(
    data: LoginRequestDTO,
    session: SessionDep,
) -> TokenResponseDTO:
    service = LoginService.build(session)
    try:
        return await service.execute(data.email, data.password)
    except LoginService.InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
        ) from e


@router.post('/register', response_model=TokenResponseDTO)
async def register(
    data: RegisterRequestDTO,
    session: SessionDep,
) -> TokenResponseDTO:
    service = RegisterService.build(session)
    try:
        return await service.execute(
            data.username,
            data.tag,
            data.email,
            data.password,
        )
    except RegisterService.TagAlreadyTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Tag already taken',
        ) from e
    except RegisterService.EmailAlreadyTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already taken',
        ) from e
