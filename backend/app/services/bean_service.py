from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bean import CoffeeBean
from app.types.schemas.bean_schema import BeanCreate, BeanOut, BeanUpdate


async def list_beans(
    session: AsyncSession,
    origin: str | None = None,
    process: str | None = None,
    flavor: str | None = None,
    search: str | None = None,
) -> list[BeanOut]:
    statement = select(CoffeeBean)
    if origin:
        statement = statement.where(CoffeeBean.origin.ilike(f"%{origin}%"))
    if process:
        statement = statement.where(CoffeeBean.process_method == process)
    if search:
        statement = statement.where(or_(CoffeeBean.name.ilike(f"%{search}%"), CoffeeBean.origin.ilike(f"%{search}%")))
    result = await session.execute(statement.order_by(CoffeeBean.id.asc()))
    beans = result.scalars().all()
    if flavor:
        beans = [bean for bean in beans if flavor in bean.flavor_tags]
    return [BeanOut.model_validate(bean) for bean in beans]


async def get_bean(session: AsyncSession, bean_id: int) -> BeanOut | None:
    bean = await session.get(CoffeeBean, bean_id)
    return BeanOut.model_validate(bean) if bean else None


async def create_bean(session: AsyncSession, payload: BeanCreate) -> BeanOut:
    bean = CoffeeBean(**payload.model_dump())
    session.add(bean)
    await session.commit()
    await session.refresh(bean)
    return BeanOut.model_validate(bean)


async def update_bean(session: AsyncSession, bean_id: int, payload: BeanUpdate) -> BeanOut | None:
    bean = await session.get(CoffeeBean, bean_id)
    if bean is None:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(bean, key, value)
    await session.commit()
    await session.refresh(bean)
    return BeanOut.model_validate(bean)


async def delete_bean(session: AsyncSession, bean_id: int) -> bool:
    bean = await session.get(CoffeeBean, bean_id)
    if bean is None:
        return False
    await session.delete(bean)
    await session.commit()
    return True
