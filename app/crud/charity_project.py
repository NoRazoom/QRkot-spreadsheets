from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject, Donation
from app.schemas.charity_project import CharityProjectUpdate


class CRUDCharity(CRUDBase):

    async def get_project_by_name(
            self,
            pr_name: str,
            session: AsyncSession
    ):
        project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == pr_name)
        )
        pr_id = project_id.scalars().first()
        return pr_id

    async def investition(
            self,
            project_id: int,
            session: AsyncSession):
        project = await self.get(project_id, session)
        pr_sum_left = project.full_amount - project.invested_amount
        donations = await session.execute(
            select(Donation).where(
                Donation.fully_invested.is_(False)
            ).order_by(Donation.create_date)
        )
        donations = donations.scalars().all()
        for donation in donations:
            don_amount_left = donation.full_amount - donation.invested_amount
            if pr_sum_left <= don_amount_left:
                project.invested_amount = project.full_amount
                project.fully_invested = True
                project.close_date = datetime.now()

                donation.invested_amount += pr_sum_left
                don_amount_left = 0
            else:
                project.invested_amount += don_amount_left
                donation.invested_amount = donation.full_amount
                donation.fully_invested = True
                donation.close_date = datetime.now()
                pr_sum_left -= don_amount_left

        session.add(project)
        await session.commit()
        await session.refresh(project)

        return project

    async def close_or_not_project(
            self,
            project: CharityProject,
            project_in: CharityProjectUpdate,
            session: AsyncSession
    ):
        if project.invested_amount == project_in.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
            session.add(project)
            await session.commit()
            await session.refresh(project)
        return project

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ):
        prods = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        projects = prods.scalars().all()
        return [
            {
                'name': project.name,
                'create_date': project.create_date,
                'close_date': project.close_date,
                'description': project.description
            }
            for project in projects
        ]


charity_project_crud = CRUDCharity(CharityProject)
