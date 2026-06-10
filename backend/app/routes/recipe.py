from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import recipe_controller
from app.database import get_session
from app.middlewares.auth import optional_user, require_auth
from app.models.user import User
from app.types.schemas.recipe_schema import RecipeCreate, RecipeUpdate
from app.utils.response import success_response

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("")
async def recipes(
    device: str | None = None,
    temp_min: float | None = Query(default=None, ge=60, le=100),
    temp_max: float | None = Query(default=None, ge=60, le=100),
    search: str | None = Query(default=None, max_length=100),
    user_id: str | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(optional_user),
):
    resolved_user_id = _resolve_user_id(user_id, current_user)
    data = await recipe_controller.list_recipes(session, device, temp_min, temp_max, search, resolved_user_id)
    return success_response(data)


@router.get("/{recipe_id}")
async def recipe_detail(recipe_id: int, session: AsyncSession = Depends(get_session)):
    return success_response(await recipe_controller.get_recipe(session, recipe_id))


@router.post("")
async def create_recipe(
    payload: RecipeCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    return success_response(await recipe_controller.create_recipe(session, payload, current_user), "配方已创建")


@router.put("/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    payload: RecipeUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    data = await recipe_controller.update_recipe(session, recipe_id, payload, current_user)
    return success_response(data, "配方已更新")


@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_auth),
):
    return success_response(await recipe_controller.delete_recipe(session, recipe_id, current_user), "配方已删除")


def _resolve_user_id(user_id: str | None, current_user: User | None) -> int | None:
    if user_id is None:
        return None
    if user_id == "me":
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
        return current_user.id
    return int(user_id)

