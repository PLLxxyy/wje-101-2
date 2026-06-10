from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.types.enums import RoastLevel
from app.types.schemas.recipe_schema import RecipeOut
from app.types.schemas.user_schema import UserPublic


class NoteBase(BaseModel):
    coffee_name: str = Field(min_length=2, max_length=100)
    origin: str = Field(min_length=2, max_length=100)
    roast_level: RoastLevel
    flavor_tags: list[str] = Field(min_length=1, max_length=12)
    aroma_score: int = Field(ge=1, le=10)
    acidity_score: int = Field(ge=1, le=10)
    body_score: int = Field(ge=1, le=10)
    overall_score: int = Field(ge=1, le=10)
    brew_method: str = Field(min_length=2, max_length=50)
    brew_recipe_id: int | None = None
    coffee_bean_id: int | None = None
    notes_text: str = Field(min_length=5, max_length=5000)
    image_url: str | None = Field(default=None, max_length=255)


class NoteCreate(NoteBase):
    model_config = ConfigDict(extra="forbid")


class NoteUpdate(BaseModel):
    coffee_name: str | None = Field(default=None, min_length=2, max_length=100)
    origin: str | None = Field(default=None, min_length=2, max_length=100)
    roast_level: RoastLevel | None = None
    flavor_tags: list[str] | None = Field(default=None, min_length=1, max_length=12)
    aroma_score: int | None = Field(default=None, ge=1, le=10)
    acidity_score: int | None = Field(default=None, ge=1, le=10)
    body_score: int | None = Field(default=None, ge=1, le=10)
    overall_score: int | None = Field(default=None, ge=1, le=10)
    brew_method: str | None = Field(default=None, min_length=2, max_length=50)
    brew_recipe_id: int | None = None
    coffee_bean_id: int | None = None
    notes_text: str | None = Field(default=None, min_length=5, max_length=5000)
    image_url: str | None = Field(default=None, max_length=255)


class NoteOut(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: UserPublic | None = None
    brew_recipe: RecipeOut | None = None
    likes_count: int = 0
    comments_count: int = 0
    liked_by_me: bool = False


class PaginatedNotes(BaseModel):
    items: list[NoteOut]
    total: int
    page: int
    page_size: int
