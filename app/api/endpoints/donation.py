from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.donation import (DonationDB, DonationCreate,
                                  DonationDBCreateNOUser)
from app.crud.donation import donation_crud
from app.models import User
from app.core.user import current_user, current_superuser


router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(session: SessionDep):
    """Показать список всех пожертвований."""
    return await donation_crud.get_multi(session)


@router.post(
    '/',
    response_model=DonationDBCreateNOUser,
    response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: Annotated[User, Depends(current_user)]
):
    """Создать пожертвование."""
    donation = await donation_crud.create(donation, session, user)
    return await donation_crud.investition(donation.id, session)


@router.get(
    '/my',
    response_model=list[DonationDBCreateNOUser],
    # использую другую схему (без user_id), посколько response_model_exclude
    # не работает
)
async def get_my_donations(
    user: Annotated[User, Depends(current_user)],
    session: SessionDep
):
    return await donation_crud.get_by_user(user, session)
