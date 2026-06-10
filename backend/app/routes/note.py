from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import note_controller
from app.database import get_session
from app.middlewares.auth import optional_user, require_auth
from app.models.user import User
from app.services import note_service
from app.types.schemas.note_schema import NoteCreate, NoteUpdate
from app.utils.response import success_response

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("")
async def notes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    roast_level: str | None = None,
    origin: str | None = None,
    user_id: int | None = None,
    search: str | None = Query(default=None, max_length=100),
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(optional_user),
):
    data = await note_controller.list_notes(
        session, page, page_size, current_user, roast_level, origin, user_id, search
    )
    return success_response(data)


@router.get("/popular")
async def popular_notes(
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(optional_user),
):
    return success_response(await note_controller.list_popular(session, limit, current_user))


@router.get("/{note_id}")
async def note_detail(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(optional_user),
):
    return success_response(await note_controller.get_note(session, note_id, current_user))


@router.post("")
async def create_note(
    payload: NoteCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    return success_response(await note_controller.create_note(session, payload, current_user), "笔记已创建")


@router.put("/{note_id}")
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    return success_response(await note_controller.update_note(session, note_id, payload, current_user), "笔记已更新")


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    return success_response(await note_controller.delete_note(session, note_id, current_user), "笔记已删除")


@router.post("/{note_id}/like")
async def like_note(note_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(require_auth)):
    await note_service.like_note(session, note_id, current_user.id)
    return success_response({"liked": True}, "已点赞")


@router.delete("/{note_id}/like")
async def unlike_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    await note_service.unlike_note(session, note_id, current_user.id)
    return success_response({"liked": False}, "已取消点赞")

