from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middlewares.auth import require_auth
from app.models.user import User
from app.services import comment_service
from app.types.schemas.comment_schema import CommentCreate, CommentUpdate
from app.utils.response import success_response

router = APIRouter(tags=["comments"])


@router.get("/api/notes/{note_id}/comments")
async def comments(note_id: int, session: AsyncSession = Depends(get_session)):
    return success_response(await comment_service.list_comments(session, note_id))


@router.post("/api/notes/{note_id}/comments")
async def create_comment(
    note_id: int,
    payload: CommentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    comment = await comment_service.create_comment(session, note_id, payload, current_user.id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")
    return success_response(comment, "评论已发布")


@router.put("/api/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    comment = await comment_service.update_comment(session, comment_id, payload, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在或无权限")
    return success_response(comment, "评论已更新")


@router.delete("/api/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    deleted = await comment_service.delete_comment(session, comment_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在或无权限")
    return success_response(True, "评论已删除")

