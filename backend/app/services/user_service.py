from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import TastingNote
from app.models.user import User, UserFollow
from app.types.enums import UserRole
from app.types.schemas.user_schema import UserCreate, UserProfile, UserPublic, UserStats, UserUpdate
from app.utils.security import hash_password, verify_password


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def list_users(session: AsyncSession) -> list[UserPublic]:
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    return [UserPublic.model_validate(user) for user in result.scalars().all()]


async def create_user(session: AsyncSession, payload: UserCreate, role: str = UserRole.user) -> User:
    user = User(
        username=payload.username,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        avatar=payload.avatar,
        bio=payload.bio,
        role=str(role),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(session, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


async def update_user(session: AsyncSession, user_id: int, payload: UserUpdate) -> User | None:
    user = await session.get(User, user_id)
    if user is None:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    user = await session.get(User, user_id)
    if user is None:
        return False
    await session.delete(user)
    await session.commit()
    return True


async def get_profile(session: AsyncSession, user_id: int, current_user_id: int | None) -> UserProfile | None:
    user = await session.get(User, user_id)
    if user is None:
        return None
    stats = await _build_stats(session, user_id, current_user_id)
    return UserProfile(user=UserPublic.model_validate(user), stats=stats)


async def follow_user(session: AsyncSession, follower_id: int, following_id: int) -> bool:
    if follower_id == following_id:
        return False
    existing = await session.get(UserFollow, {"follower_id": follower_id, "following_id": following_id})
    if existing is None:
        session.add(UserFollow(follower_id=follower_id, following_id=following_id))
        await session.commit()
    return True


async def unfollow_user(session: AsyncSession, follower_id: int, following_id: int) -> bool:
    statement = delete(UserFollow).where(
        and_(UserFollow.follower_id == follower_id, UserFollow.following_id == following_id)
    )
    await session.execute(statement)
    await session.commit()
    return True


async def _build_stats(session: AsyncSession, user_id: int, current_user_id: int | None) -> UserStats:
    note_count = await session.scalar(select(func.count()).select_from(TastingNote).where(TastingNote.user_id == user_id))
    average_score = await session.scalar(select(func.avg(TastingNote.overall_score)).where(TastingNote.user_id == user_id))
    following_count = await session.scalar(select(func.count()).select_from(UserFollow).where(UserFollow.follower_id == user_id))
    follower_count = await session.scalar(select(func.count()).select_from(UserFollow).where(UserFollow.following_id == user_id))
    origins_result = await session.execute(
        select(TastingNote.origin, func.count(TastingNote.id).label("total"))
        .where(TastingNote.user_id == user_id)
        .group_by(TastingNote.origin)
        .order_by(func.count(TastingNote.id).desc())
        .limit(3)
    )
    radar_result = await session.execute(
        select(
            func.avg(TastingNote.aroma_score),
            func.avg(TastingNote.acidity_score),
            func.avg(TastingNote.body_score),
            func.avg(TastingNote.overall_score),
        ).where(TastingNote.user_id == user_id)
    )
    radar_row = radar_result.one()
    is_following = False
    if current_user_id:
        follow = await session.get(UserFollow, {"follower_id": current_user_id, "following_id": user_id})
        is_following = follow is not None
    radar_scores = {
        "aroma": round(float(radar_row[0] or 0), 1),
        "acidity": round(float(radar_row[1] or 0), 1),
        "body": round(float(radar_row[2] or 0), 1),
        "overall": round(float(radar_row[3] or 0), 1),
    }
    return UserStats(
        note_count=int(note_count or 0),
        average_score=round(float(average_score or 0), 1),
        top_origins=[row[0] for row in origins_result.all()],
        radar_scores=radar_scores,
        following_count=int(following_count or 0),
        follower_count=int(follower_count or 0),
        is_following=is_following,
    )

