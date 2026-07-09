from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, CharityProject, User


class CRUDDonation(CRUDBase):

    async def investition(
            self,
            donation_id: int,
            session: AsyncSession
    ):
        donation = await self.get(donation_id, session)
        donation_left_amount = donation.full_amount
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(False)
            ).order_by(CharityProject.create_date)
        )
        projects_list = projects.scalars().all()
        for project in projects_list:
            project_sum_left = project.full_amount - project.invested_amount
            if project_sum_left <= donation_left_amount:
                project.invested_amount = project.full_amount
                project.fully_invested = True
                project.close_date = datetime.now()
                donation_left_amount -= project_sum_left
            else:
                project.invested_amount += donation_left_amount
                donation_left_amount = 0

        if donation_left_amount == 0:
            donation.fully_invested = True
            donation.close_date = datetime.now()
            donation.invested_amount = donation.full_amount
        else:
            donation.invested_amount = (
                donation.full_amount - donation_left_amount)

        session.add(donation)
        await session.commit()
        await session.refresh(donation)

        return donation

    async def get_by_user(
            self,
            user: User,
            session: AsyncSession
    ):
        dons = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        dons = dons.scalars().all()
        return dons


donation_crud = CRUDDonation(Donation)
