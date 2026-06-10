from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    avatar: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=500)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=50)
    avatar: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=500)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    avatar: str | None
    bio: str | None
    role: str
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class UserStats(BaseModel):
    note_count: int
    average_score: float
    top_origins: list[str]
    radar_scores: dict[str, float]
    following_count: int
    follower_count: int
    is_following: bool


class UserProfile(BaseModel):
    user: UserPublic
    stats: UserStats

