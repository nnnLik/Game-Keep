from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.users import MeResponseDTO
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.users.create_banner_service import CreateBannerService
from services.users.delete_banner_service import DeleteBannerService
from services.users.me_service import MeService

router = APIRouter(prefix='/users', tags=['users'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get('/me', response_model=MeResponseDTO)
async def me(current_user: CurrentUserDep, session: SessionDep) -> MeResponseDTO:
    return await MeService.build(session).execute(current_user.id)


@router.patch('/me/banner', response_model=MeResponseDTO)
async def update_banner(
    current_user: CurrentUserDep,
    session: SessionDep,
    banner: UploadFile = File(...),
) -> MeResponseDTO:
    service = CreateBannerService.build(session)
    try:
        await service.execute(current_user.id, banner)
    except CreateBannerService.BannerTooLargeError:
        raise HTTPException(400, 'Banner too large (max 2 MB)')
    except CreateBannerService.InvalidFormatError:
        raise HTTPException(400, 'Only PNG allowed')
    return await MeService.build(session).execute(current_user.id)


@router.delete('/me/banner', response_model=MeResponseDTO)
async def delete_banner(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MeResponseDTO:
    await DeleteBannerService.build(session).execute(current_user.id)
    return await MeService.build(session).execute(current_user.id)
