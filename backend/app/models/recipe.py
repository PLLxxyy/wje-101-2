from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BrewRecipe(Base):
    __tablename__ = "brew_recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    device: Mapped[str] = mapped_column(String(50), index=True)
    water_temp: Mapped[float] = mapped_column(Float)
    grind_size: Mapped[str] = mapped_column(String(50))
    ratio: Mapped[str] = mapped_column(String(20))
    steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="recipes")
    notes = relationship("TastingNote", back_populates="brew_recipe")

