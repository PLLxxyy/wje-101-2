from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.services import user_service
from app.types.schemas.user_schema import RefreshRequest, TokenPair, UserCreate, UserLogin, UserPublic
from app.utils.response import success_response
from app.utils.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    if await user_service.get_user_by_email(session, str(payload.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已注册")
    if await user_service.get_user_by_username(session, payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user = await user_service.create_user(session, payload)
    return success_response(UserPublic.model_validate(user), "注册成功")


@router.post("/login")
async def login(payload: UserLogin, session: AsyncSession = Depends(get_session)):
    user = await user_service.authenticate_user(session, str(payload.email), payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")
    token_pair = TokenPair(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
        user=UserPublic.model_validate(user),
    )
    return success_response(token_pair, "登录成功")


@router.post("/refresh")
async def refresh_token(payload: RefreshRequest, session: AsyncSession = Depends(get_session)):
    decoded = decode_token(payload.refresh_token, "refresh")
    if decoded is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌无效")
    user = await session.get(User, int(decoded["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    token_pair = TokenPair(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
        user=UserPublic.model_validate(user),
    )
    return success_response(token_pair, "刷新成功")
