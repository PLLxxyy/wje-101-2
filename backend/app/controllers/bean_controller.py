from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import bean_service
from app.types.schemas.bean_schema import BeanCreate, BeanOut, BeanUpdate


async def list_beans(
    session: AsyncSession,
    origin: str | None,
    process: str | None,
    flavor: str | None,
    search: str | None,
) -> list[BeanOut]:
    return await bean_service.list_beans(session, origin, process, flavor, search)


async def get_bean(session: AsyncSession, bean_id: int) -> BeanOut:
    bean = await bean_service.get_bean(session, bean_id)
    if bean is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="豆种不存在")
    return bean


async def create_bean(session: AsyncSession, payload: BeanCreate) -> BeanOut:
    return await bean_service.create_bean(session, payload)


async def update_bean(session: AsyncSession, bean_id: int, payload: BeanUpdate) -> BeanOut:
    bean = await bean_service.update_bean(session, bean_id, payload)
    if bean is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="豆种不存在")
    return bean


async def delete_bean(session: AsyncSession, bean_id: int) -> bool:
    deleted = await bean_service.delete_bean(session, bean_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="豆种不存在")
    return deleted

