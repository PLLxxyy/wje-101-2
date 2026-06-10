from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recipe import BrewRecipe
from app.models.user import User
from app.types.enums import UserRole
from app.types.schemas.recipe_schema import RecipeCreate, RecipeOut, RecipeUpdate


async def list_recipes(
    session: AsyncSession,
    device: str | None = None,
    temp_min: float | None = None,
    temp_max: float | None = None,
    search: str | None = None,
    user_id: int | None = None,
) -> list[RecipeOut]:
    statement = select(BrewRecipe).options(selectinload(BrewRecipe.user))
    if device:
        statement = statement.where(BrewRecipe.device.ilike(f"%{device}%"))
    if temp_min is not None:
        statement = statement.where(BrewRecipe.water_temp >= temp_min)
    if temp_max is not None:
        statement = statement.where(BrewRecipe.water_temp <= temp_max)
    if search:
        statement = statement.where(BrewRecipe.name.ilike(f"%{search}%"))
    if user_id:
        statement = statement.where(BrewRecipe.user_id == user_id)
    result = await session.execute(statement.order_by(BrewRecipe.created_at.desc()))
    return [RecipeOut.model_validate(recipe) for recipe in result.scalars().all()]


async def get_recipe(session: AsyncSession, recipe_id: int) -> RecipeOut | None:
    statement = select(BrewRecipe).options(selectinload(BrewRecipe.user)).where(BrewRecipe.id == recipe_id)
    result = await session.execute(statement)
    recipe = result.scalar_one_or_none()
    return RecipeOut.model_validate(recipe) if recipe else None


async def create_recipe(session: AsyncSession, payload: RecipeCreate, user_id: int) -> RecipeOut:
    data = payload.model_dump(mode="json")
    recipe = BrewRecipe(user_id=user_id, **data)
    session.add(recipe)
    await session.commit()
    statement = select(BrewRecipe).options(selectinload(BrewRecipe.user)).where(BrewRecipe.id == recipe.id)
    result = await session.execute(statement)
    return RecipeOut.model_validate(result.scalar_one())


async def update_recipe(
    session: AsyncSession, recipe_id: int, payload: RecipeUpdate, current_user: User
) -> RecipeOut | None:
    recipe = await session.get(BrewRecipe, recipe_id)
    if recipe is None or not _can_modify(recipe.user_id, current_user):
        return None
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(recipe, key, value)
    await session.commit()
    return await get_recipe(session, recipe_id)


async def delete_recipe(session: AsyncSession, recipe_id: int, current_user: User) -> bool:
    recipe = await session.get(BrewRecipe, recipe_id)
    if recipe is None or not _can_modify(recipe.user_id, current_user):
        return False
    await session.delete(recipe)
    await session.commit()
    return True


def _can_modify(owner_id: int, user: User) -> bool:
    return owner_id == user.id or user.role == UserRole.admin

