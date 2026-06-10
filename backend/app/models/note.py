from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TastingNote(Base):
    __tablename__ = "tasting_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    coffee_name: Mapped[str] = mapped_column(String(100), index=True)
    origin: Mapped[str] = mapped_column(String(100), index=True)
    roast_level: Mapped[str] = mapped_column(String(20), index=True)
    flavor_tags: Mapped[list[str]] = mapped_column(JSON)
    aroma_score: Mapped[int]
    acidity_score: Mapped[int]
    body_score: Mapped[int]
    overall_score: Mapped[int]
    brew_method: Mapped[str] = mapped_column(String(50))
    brew_recipe_id: Mapped[int | None] = mapped_column(ForeignKey("brew_recipes.id", ondelete="SET NULL"))
    coffee_bean_id: Mapped[int | None] = mapped_column(ForeignKey("coffee_beans.id", ondelete="SET NULL"))
    notes_text: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="notes")
    brew_recipe = relationship("BrewRecipe", back_populates="notes")
    comments = relationship("Comment", back_populates="note", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="note", cascade="all, delete-orphan")


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("user_id", "note_id", name="uq_user_note_like"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("tasting_notes.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="likes")
    note = relationship("TastingNote", back_populates="likes")

