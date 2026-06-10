from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import user_controller
from app.database import get_session
from app.middlewares.auth import optional_user, require_admin, require_auth
from app.models.user import User
from app.services import user_service
from app.types.schemas.user_schema import UserPublic, UserUpdate
from app.utils.response import success_response

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
async def users(session: AsyncSession = Depends(get_session), admin: User = Depends(require_admin)):
    return success_response(await user_controller.list_users(session))


@router.get("/me")
async def me(current_user: User = Depends(require_auth)):
    return success_response(UserPublic.model_validate(current_user))


@router.get("/{user_id}")
async def profile(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(optional_user),
):
    return success_response(await user_controller.get_profile(session, user_id, current_user))


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    return success_response(await user_controller.update_user(session, user_id, payload, current_user), "资料已更新")


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session), admin: User = Depends(require_admin)):
    return success_response(await user_controller.delete_user(session, user_id), "用户已删除")


@router.post("/{user_id}/follow")
async def follow_user(user_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(require_auth)):
    ok = await user_service.follow_user(session, current_user.id, user_id)
    return success_response({"following": ok}, "已关注")


@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    await user_service.unfollow_user(session, current_user.id, user_id)
    return success_response({"following": False}, "已取消关注")

