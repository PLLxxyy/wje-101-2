from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services import user_service
from app.types.enums import UserRole
from app.types.schemas.user_schema import UserProfile, UserPublic, UserUpdate


async def list_users(session: AsyncSession) -> list[UserPublic]:
    return await user_service.list_users(session)


async def get_profile(session: AsyncSession, user_id: int, current_user: User | None) -> UserProfile:
    current_id = current_user.id if current_user else None
    profile = await user_service.get_profile(session, user_id, current_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return profile


async def update_user(session: AsyncSession, user_id: int, payload: UserUpdate, current_user: User) -> UserPublic:
    if current_user.id != user_id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能修改自己的资料")
    user = await user_service.update_user(session, user_id, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return UserPublic.model_validate(user)


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    deleted = await user_service.delete_user(session, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return deleted

