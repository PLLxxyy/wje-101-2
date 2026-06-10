from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.types.schemas.user_schema import UserPublic


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    note_id: int
    user_id: int
    content: str
    created_at: datetime
    user: UserPublic | None = None

