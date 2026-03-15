from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.auth import (
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
    except RegisterService.UsernameTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Имя пользователя должно быть не менее 5 символов',
        ) from e
    except RegisterService.TagTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тег должен быть от 3 до 15 символов',
        ) from e
    except RegisterService.TagTooLongError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тег должен быть от 3 до 15 символов',
        ) from e
    except RegisterService.TagInvalidCharactersError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тег может содержать только буквы и цифры',
        ) from e
    except RegisterService.TagAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тег уже занят',
        )
    except RegisterService.EmailAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email уже занят',
        )


@router.post('/register-start', response_model=TokenResponseDTO)
async def register_start(
    data: RegisterStartRequestDTO,
    session: SessionDep,
) -> TokenResponseDTO:
    service = RegisterStartService.build(session)
    try:
        return await service.execute(data.email, data.password)
    except RegisterStartService.PasswordTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пароль должен быть не менее 8 символов',
        ) from e
    except RegisterStartService.EmailAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email уже занят',
        )


@router.post('/complete-registration')
async def complete_registration(
    session: SessionDep,
    current_user: CurrentUserDep,
    username: str = Form(...),
    tag: str = Form(...),
    avatar: UploadFile | None = File(None),
) -> dict:
    service = CompleteRegistrationService.build(session)
    try:
        await service.execute(
            user_id=current_user.id,
            username=username,
            tag=tag,
            avatar=avatar,
        )
    except CompleteRegistrationService.UsernameTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Имя пользователя должно быть не менее 5 символов',
        ) from e
    except CompleteRegistrationService.TagTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тег должен быть от 3 до 15 символов',
        ) from e
    except CompleteRegistrationService.TagAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тег уже занят',
        )
    except CompleteRegistrationService.UserAlreadyCompleteError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Регистрация уже завершена',
        )
    except CompleteRegistrationService.AvatarInvalidFormatError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Неверный формат аватара. Допустимы: {", ".join(CompleteRegistrationService.ALLOWED_EXTENSIONS)}',
        )
    except CompleteRegistrationService.AvatarTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Аватар слишком большой (макс. 25 МБ)',
        )

    return {'ok': True}
