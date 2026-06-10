from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(subject: str, role: str, expires_minutes: int, token_type: str) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {"sub": subject, "role": role, "type": token_type, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int, role: str) -> str:
    settings = get_settings()
    return create_token(str(user_id), role, settings.access_token_expire_minutes, "access")


def create_refresh_token(user_id: int, role: str) -> str:
    settings = get_settings()
    return create_token(str(user_id), role, settings.refresh_token_expire_minutes, "refresh")


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any] | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload

