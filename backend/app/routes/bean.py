from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import bean_controller
from app.database import get_session
from app.middlewares.auth import require_admin
from app.models.user import User
from app.types.schemas.bean_schema import BeanCreate, BeanUpdate
from app.utils.response import success_response

router = APIRouter(prefix="/api/beans", tags=["beans"])


@router.get("")
async def beans(
    origin: str | None = None,
    process: str | None = None,
    flavor: str | None = None,
    search: str | None = Query(default=None, max_length=100),
    session: AsyncSession = Depends(get_session),
):
    data = await bean_controller.list_beans(session, origin, process, flavor, search)
    return success_response(data)


@router.get("/{bean_id}")
async def bean_detail(bean_id: int, session: AsyncSession = Depends(get_session)):
    return success_response(await bean_controller.get_bean(session, bean_id))


@router.post("")
async def create_bean(
    payload: BeanCreate,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
):
    return success_response(await bean_controller.create_bean(session, payload), "豆种已新增")


@router.put("/{bean_id}")
async def update_bean(
    bean_id: int,
    payload: BeanUpdate,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
):
    return success_response(await bean_controller.update_bean(session, bean_id, payload), "豆种已更新")


@router.delete("/{bean_id}")
async def delete_bean(
    bean_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
):
    return success_response(await bean_controller.delete_bean(session, bean_id), "豆种已删除")

