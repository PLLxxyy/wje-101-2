from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.note import TastingNote
from app.models.user import User
from app.types.enums import UserRole
from app.types.schemas.comment_schema import CommentCreate, CommentOut, CommentUpdate


async def list_comments(session: AsyncSession, note_id: int) -> list[CommentOut]:
    statement = select(Comment).options(selectinload(Comment.user)).where(Comment.note_id == note_id)
    result = await session.execute(statement.order_by(Comment.created_at.asc()))
    return [CommentOut.model_validate(comment) for comment in result.scalars().all()]


async def create_comment(session: AsyncSession, note_id: int, payload: CommentCreate, user_id: int) -> CommentOut | None:
    note = await session.get(TastingNote, note_id)
    if note is None:
        return None
    comment = Comment(note_id=note_id, user_id=user_id, content=payload.content)
    session.add(comment)
    await session.commit()
    statement = select(Comment).options(selectinload(Comment.user)).where(Comment.id == comment.id)
    result = await session.execute(statement)
    return CommentOut.model_validate(result.scalar_one())


async def update_comment(
    session: AsyncSession, comment_id: int, payload: CommentUpdate, current_user: User
) -> CommentOut | None:
    comment = await session.get(Comment, comment_id)
    if comment is None or not _can_modify(comment.user_id, current_user):
        return None
    comment.content = payload.content
    await session.commit()
    result = await session.execute(select(Comment).options(selectinload(Comment.user)).where(Comment.id == comment_id))
    return CommentOut.model_validate(result.scalar_one())


async def delete_comment(session: AsyncSession, comment_id: int, current_user: User) -> bool:
    comment = await session.get(Comment, comment_id)
    if comment is None or not _can_modify(comment.user_id, current_user):
        return False
    await session.delete(comment)
    await session.commit()
    return True


def _can_modify(owner_id: int, user: User) -> bool:
    return owner_id == user.id or user.role == UserRole.admin

