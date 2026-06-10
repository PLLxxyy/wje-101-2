from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+asyncpg://coffeetaste:coffeetaste_pwd@db:5432/coffeetaste",
        alias="DATABASE_URL",
    )
    jwt_secret: str = Field(default="change_me_to_a_long_random_string", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 45
    refresh_token_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "http://localhost:28601,http://127.0.0.1:28601"


@lru_cache
def get_settings() -> Settings:
    return Settings()

