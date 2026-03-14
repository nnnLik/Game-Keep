from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.auth import LoginRequestDTO, RegisterRequestDTO, TokenResponseDTO
from infra.db import get_db
from services.auth import LoginService, RegisterService

router = APIRouter(prefix='/auth', tags=['auth'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post('/login', response_model=TokenResponseDTO)
async def login(
    data: LoginRequestDTO,
    session: SessionDep,
) -> TokenResponseDTO:
    service = LoginService.build(session)
    try:
        return await service.execute(data)
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
        return await service.execute(data)
    except RegisterService.UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists',
        ) from e
