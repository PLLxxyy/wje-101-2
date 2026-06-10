from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.note import Like, TastingNote
from app.models.recipe import BrewRecipe
from app.models.user import User
from app.types.enums import UserRole
from app.types.schemas.note_schema import NoteCreate, NoteOut, NoteUpdate, PaginatedNotes


async def list_notes(
    session: AsyncSession,
    page: int,
    page_size: int,
    current_user_id: int | None = None,
    roast_level: str | None = None,
    origin: str | None = None,
    user_id: int | None = None,
    search: str | None = None,
) -> PaginatedNotes:
    conditions = _note_conditions(roast_level, origin, user_id, search)
    total = await session.scalar(select(func.count()).select_from(TastingNote).where(*conditions))
    statement = _note_query().where(*conditions).order_by(TastingNote.created_at.desc())
    result = await session.execute(statement.offset((page - 1) * page_size).limit(page_size))
    items = [await _note_out(session, note, current_user_id) for note in result.scalars().all()]
    return PaginatedNotes(items=items, total=int(total or 0), page=page, page_size=page_size)


async def list_popular(session: AsyncSession, limit: int, current_user_id: int | None = None) -> list[NoteOut]:
    statement = (
        _note_query()
        .outerjoin(Like, Like.note_id == TastingNote.id)
        .group_by(TastingNote.id)
        .order_by(func.count(Like.id).desc(), TastingNote.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(statement)
    return [await _note_out(session, note, current_user_id) for note in result.scalars().unique().all()]


async def get_note(session: AsyncSession, note_id: int, current_user_id: int | None = None) -> NoteOut | None:
    result = await session.execute(_note_query().where(TastingNote.id == note_id))
    note = result.scalar_one_or_none()
    return await _note_out(session, note, current_user_id) if note else None


async def create_note(session: AsyncSession, payload: NoteCreate, user_id: int) -> NoteOut:
    note = TastingNote(user_id=user_id, **payload.model_dump(mode="json"))
    session.add(note)
    await session.commit()
    await session.refresh(note)
    created = await get_note(session, note.id, user_id)
    if created is None:
        raise RuntimeError("笔记创建后读取失败")
    return created


async def update_note(session: AsyncSession, note_id: int, payload: NoteUpdate, current_user: User) -> NoteOut | None:
    note = await session.get(TastingNote, note_id)
    if note is None or not _can_modify(note.user_id, current_user):
        return None
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(note, key, value)
    await session.commit()
    return await get_note(session, note_id, current_user.id)


async def delete_note(session: AsyncSession, note_id: int, current_user: User) -> bool:
    note = await session.get(TastingNote, note_id)
    if note is None or not _can_modify(note.user_id, current_user):
        return False
    await session.delete(note)
    await session.commit()
    return True


async def like_note(session: AsyncSession, note_id: int, user_id: int) -> bool:
    note = await session.get(TastingNote, note_id)
    if note is None:
        return False
    existing = await session.execute(select(Like).where(and_(Like.note_id == note_id, Like.user_id == user_id)))
    if existing.scalar_one_or_none() is None:
        session.add(Like(note_id=note_id, user_id=user_id))
        await session.commit()
    return True


async def unlike_note(session: AsyncSession, note_id: int, user_id: int) -> bool:
    await session.execute(delete(Like).where(and_(Like.note_id == note_id, Like.user_id == user_id)))
    await session.commit()
    return True


def _note_conditions(roast_level: str | None, origin: str | None, user_id: int | None, search: str | None):
    conditions = []
    if roast_level:
        conditions.append(TastingNote.roast_level == roast_level)
    if origin:
        conditions.append(TastingNote.origin.ilike(f"%{origin}%"))
    if user_id:
        conditions.append(TastingNote.user_id == user_id)
    if search:
        conditions.append(or_(TastingNote.coffee_name.ilike(f"%{search}%"), TastingNote.notes_text.ilike(f"%{search}%")))
    return conditions


def _note_query():
    return select(TastingNote).options(
        selectinload(TastingNote.user),
        selectinload(TastingNote.brew_recipe).selectinload(BrewRecipe.user),
    )


async def _note_out(session: AsyncSession, note: TastingNote, current_user_id: int | None) -> NoteOut:
    like_count = await session.scalar(select(func.count()).select_from(Like).where(Like.note_id == note.id))
    comment_count = await session.scalar(select(func.count()).select_from(Comment).where(Comment.note_id == note.id))
    liked = False
    if current_user_id:
        liked_query = select(Like).where(and_(Like.note_id == note.id, Like.user_id == current_user_id))
        liked = (await session.execute(liked_query)).scalar_one_or_none() is not None
    base = NoteOut.model_validate(note)
    base.likes_count = int(like_count or 0)
    base.comments_count = int(comment_count or 0)
    base.liked_by_me = liked
    return base


def _can_modify(owner_id: int, user: User) -> bool:
    return owner_id == user.id or user.role == UserRole.admin
