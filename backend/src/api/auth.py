from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.auth import (
    CompleteRegistrationRequestDTO,
    LoginRequestDTO,
    RefreshRequestDTO,
    RegisterRequestDTO,
    RegisterStartRequestDTO,
    TokenResponseDTO,
)
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.auth import (
    CompleteRegistrationService,
    LoginService,
    RefreshTokenService,
    RegisterService,
    RegisterStartService,
)

router = APIRouter(prefix='/auth', tags=['auth'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


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


@router.post('/register-start', response_model=TokenResponseDTO)
async def register_start(
    data: RegisterStartRequestDTO,
    session: SessionDep,
) -> TokenResponseDTO:
    service = RegisterStartService.build(session)
    try:
        return await service.execute(data.email, data.password)
    except RegisterStartService.EmailAlreadyTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already taken',
        ) from e


@router.post('/complete-registration')
async def complete_registration(
    session: SessionDep,
    current_user: CurrentUserDep,
    username: str = Form(...),
    tag: str = Form(...),
    avatar: UploadFile | None = File(None),
) -> dict:
    data = CompleteRegistrationRequestDTO(username=username, tag=tag)
    service = CompleteRegistrationService.build(session)
    try:
        await service.execute(
            user_id=current_user.id,
            username=data.username,
            tag=data.tag,
            avatar=avatar,
        )
    except CompleteRegistrationService.TagAlreadyTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Tag already taken',
        ) from e
    except CompleteRegistrationService.UserAlreadyCompleteError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Registration already complete',
        ) from e
    except CompleteRegistrationService.AvatarInvalidFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid avatar format. Allowed: {", ".join(CompleteRegistrationService.ALLOWED_EXTENSIONS)}',
        ) from e
    except CompleteRegistrationService.AvatarTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Avatar too large (max 5 MB)',
        ) from e

    return {'ok': True}
