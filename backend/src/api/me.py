from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.users import MeResponseDTO
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.users.me_service import MeService

router = APIRouter(prefix='/users', tags=['users'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get('/me', response_model=MeResponseDTO)
async def me(current_user: CurrentUserDep, session: SessionDep) -> MeResponseDTO:
    return await MeService.build(session).execute(current_user.id)
