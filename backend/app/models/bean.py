from typing import Any

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CoffeeBean(Base):
    __tablename__ = "coffee_beans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    origin: Mapped[str] = mapped_column(String(100), index=True)
    process_method: Mapped[str] = mapped_column(String(50), index=True)
    flavor_tags: Mapped[list[str]] = mapped_column(JSON)
    description: Mapped[str] = mapped_column(Text)

