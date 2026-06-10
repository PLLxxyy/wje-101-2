from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services import note_service
from app.types.schemas.note_schema import NoteCreate, NoteOut, NoteUpdate, PaginatedNotes


async def list_notes(
    session: AsyncSession,
    page: int,
    page_size: int,
    current_user: User | None,
    roast_level: str | None,
    origin: str | None,
    user_id: int | None,
    search: str | None,
) -> PaginatedNotes:
    current_id = current_user.id if current_user else None
    return await note_service.list_notes(session, page, page_size, current_id, roast_level, origin, user_id, search)


async def list_popular(session: AsyncSession, limit: int, current_user: User | None) -> list[NoteOut]:
    current_id = current_user.id if current_user else None
    return await note_service.list_popular(session, limit, current_id)


async def get_note(session: AsyncSession, note_id: int, current_user: User | None) -> NoteOut:
    current_id = current_user.id if current_user else None
    note = await note_service.get_note(session, note_id, current_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")
    return note


async def create_note(session: AsyncSession, payload: NoteCreate, current_user: User) -> NoteOut:
    return await note_service.create_note(session, payload, current_user.id)


async def update_note(session: AsyncSession, note_id: int, payload: NoteUpdate, current_user: User) -> NoteOut:
    note = await note_service.update_note(session, note_id, payload, current_user)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在或无权限")
    return note


async def delete_note(session: AsyncSession, note_id: int, current_user: User) -> bool:
    deleted = await note_service.delete_note(session, note_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在或无权限")
    return deleted

