from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.charity_project import (CharityProjectDB,
                                         CharityProjectCreate,
                                         CharityProjectUpdate)
from app.crud.charity_project import charity_project_crud
from app.api.validators import (check_unique_name, check_project_before_delete,
                                check_project_exists, check_project_closed,
                                check_edit_sum)
from app.core.user import current_superuser


router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_projects(session: SessionDep):
    """Показать список всех целевых проектов."""
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_project(
    project: CharityProjectCreate,
    session: SessionDep
):
    """Создать целевой проект."""
    await check_unique_name(project.name, session)
    project = await charity_project_crud.create(project, session)
    return await charity_project_crud.investition(project.id, session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def remove_project(
    project_id: int,
    session: SessionDep
):
    """
    Удалить целевой проект.
    Нельзя удалить проект, в который уже были инвестированы средства.
    """
    project = await check_project_exists(project_id, session)
    project = await check_project_before_delete(project_id, session)
    return await charity_project_crud.remove(project, session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def update_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep
):
    """
    Редактировать целевой проект.
    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    project = await check_project_exists(project_id, session)
    if obj_in.name is not None:
        await check_unique_name(obj_in.name, session)
    await check_project_closed(project_id, session)
    project = await check_edit_sum(project_id, obj_in, session)
    if obj_in.full_amount is not None:
        project = await charity_project_crud.close_or_not_project(
            project, obj_in, session
        )

    return await charity_project_crud.update(project, obj_in, session)
