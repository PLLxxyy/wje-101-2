from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.types.enums import UserRole
from app.utils.security import decode_token


async def auth_middleware(request: Request, call_next: Callable[[Request], Awaitable[object]]) -> object:
    request.state.user_id = None
    request.state.role = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        payload = decode_token(token)
        if payload:
            request.state.user_id = int(payload["sub"])
            request.state.role = str(payload["role"])
    return await call_next(request)


async def require_auth(request: Request, session: AsyncSession = Depends(get_session)) -> User:
    if request.state.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    user = await session.get(User, int(request.state.user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


async def optional_user(request: Request, session: AsyncSession = Depends(get_session)) -> User | None:
    if request.state.user_id is None:
        return None
    result = await session.execute(select(User).where(User.id == int(request.state.user_id)))
    return result.scalar_one_or_none()


async def require_admin(current_user: User = Depends(require_auth)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user

