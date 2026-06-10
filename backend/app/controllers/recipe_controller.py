from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services import recipe_service
from app.types.schemas.recipe_schema import RecipeCreate, RecipeOut, RecipeUpdate


async def list_recipes(
    session: AsyncSession,
    device: str | None,
    temp_min: float | None,
    temp_max: float | None,
    search: str | None,
    user_id: int | None,
) -> list[RecipeOut]:
    return await recipe_service.list_recipes(session, device, temp_min, temp_max, search, user_id)


async def get_recipe(session: AsyncSession, recipe_id: int) -> RecipeOut:
    recipe = await recipe_service.get_recipe(session, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配方不存在")
    return recipe


async def create_recipe(session: AsyncSession, payload: RecipeCreate, current_user: User) -> RecipeOut:
    return await recipe_service.create_recipe(session, payload, current_user.id)


async def update_recipe(
    session: AsyncSession, recipe_id: int, payload: RecipeUpdate, current_user: User
) -> RecipeOut:
    recipe = await recipe_service.update_recipe(session, recipe_id, payload, current_user)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配方不存在或无权限")
    return recipe


async def delete_recipe(session: AsyncSession, recipe_id: int, current_user: User) -> bool:
    deleted = await recipe_service.delete_recipe(session, recipe_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配方不存在或无权限")
    return deleted

