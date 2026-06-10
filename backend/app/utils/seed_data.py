from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bean import CoffeeBean
from app.models.comment import Comment
from app.models.note import Like, TastingNote
from app.models.recipe import BrewRecipe
from app.models.user import User, UserFollow
from app.utils.security import hash_password


async def seed_database(session: AsyncSession) -> None:
    existing = await session.execute(select(User).limit(1))
    if existing.scalar_one_or_none() is not None:
        return
    users = _users()
    session.add_all(users)
    await session.flush()
    beans = _beans()
    session.add_all(beans)
    await session.flush()
    recipes = _recipes(users)
    session.add_all(recipes)
    await session.flush()
    notes = _notes(users, recipes)
    session.add_all(notes)
    await session.flush()
    session.add_all(_comments(users, notes))
    session.add_all(_likes(users, notes))
    session.add_all(_follows(users))
    await session.commit()


def _users() -> list[User]:
    password = hash_password("Coffee@2026")
    return [
        User(
            username="barista_wang",
            email="wang@coffee.com",
            password_hash=password,
            role="admin",
            bio="资深咖啡师，SCA认证品鉴师",
        ),
        User(
            username="coffee_lover",
            email="lover@coffee.com",
            password_hash=password,
            role="user",
            bio="咖啡爱好者，每天至少一杯手冲",
        ),
        User(
            username="bean_hunter",
            email="hunter@coffee.com",
            password_hash=password,
            role="user",
            bio="咖啡豆猎人，游历各大产区",
        ),
    ]


def _beans() -> list[CoffeeBean]:
    return [
        CoffeeBean(name="耶加雪菲 G1", origin="埃塞俄比亚·耶加雪菲", process_method="washed", flavor_tags=["柑橘", "茉莉花", "柠檬", "茶感"], description="经典埃塞水洗豆，花香柑橘调明亮"),
        CoffeeBean(name="曼特宁 G1", origin="印度尼西亚·苏门答腊", process_method="honey", flavor_tags=["草本", "烟草", "黑巧克力", "松木"], description="浓郁醇厚的印尼代表，低酸厚重"),
        CoffeeBean(name="瑰夏", origin="巴拿马·波奎特", process_method="washed", flavor_tags=["玫瑰", "佛手柑", "蜜桃", "茉莉"], description="咖啡中的香槟，优雅花果调"),
        CoffeeBean(name="哥伦慧兰", origin="坦桑尼亚·慧兰", process_method="natural", flavor_tags=["蓝莓", "红酒", "黑莓", "可可"], description="日晒处理带来浆果般的甜美"),
        CoffeeBean(name="肯尼亚 AA", origin="肯尼亚·涅里", process_method="washed", flavor_tags=["黑加仑", "番茄", "焦糖", "西柚"], description="明亮的酸质和复杂的层次感"),
        CoffeeBean(name="巴西黄波旁", origin="巴西·米纳斯", process_method="natural", flavor_tags=["坚果", "巧克力", "焦糖", "奶油"], description="经典意式拼配基底豆，坚果甜感稳定顺滑"),
    ]


def _recipes(users: list[User]) -> list[BrewRecipe]:
    return [
        BrewRecipe(user_id=users[0].id, name="V60 经典手冲", device="V60", water_temp=92, grind_size="中细（细砂糖）", ratio="1:15", steps=_steps(["称豆15g研磨", "注水30g闷蒸30s", "注水至120g", "注水至225g", "等待滴完"])),
        BrewRecipe(user_id=users[1].id, name="法压壶浸泡", device="法压壶", water_temp=94, grind_size="粗研磨", ratio="1:12", steps=_steps(["称豆20g粗磨", "注入240g热水", "搅拌3次", "盖盖浸泡4分钟", "缓慢下压"])),
        BrewRecipe(user_id=users[0].id, name="意式浓缩", device="意式咖啡机", water_temp=93, grind_size="极细", ratio="1:2", steps=_steps(["称豆18g填压", "萃取36g浓缩", "萃取时间25-30秒"])),
    ]


def _notes(users: list[User], recipes: list[BrewRecipe]) -> list[TastingNote]:
    return [
        _note(users[1].id, "耶加雪菲·花魁", "埃塞俄比亚", "light", ["柑橘", "茉莉花", "蜜桃"], 9, 8, 6, 8, "V60 手冲", recipes[0].id, "入口有干净的柑橘酸，温度下降后蜜桃甜感浮现，尾段茶感清爽。"),
        _note(users[2].id, "曼特宁·老虎", "印度尼西亚", "dark", ["草本", "黑巧克力", "烟草"], 7, 4, 9, 7, "法压壶", recipes[1].id, "厚重油脂感明显，草本与黑巧克力贯穿始终，适合下午慢饮。"),
        _note(users[0].id, "瑰夏·翡翠庄园", "巴拿马", "light", ["玫瑰", "佛手柑", "蜜桃"], 10, 9, 7, 10, "V60 手冲", recipes[0].id, "花香非常立体，佛手柑和蜜桃香气层层展开，余韵细长。"),
        _note(users[1].id, "肯尼亚 AA·涅里", "肯尼亚", "medium", ["黑加仑", "番茄", "焦糖"], 8, 9, 7, 8, "V60 手冲", None, "酸质像黑加仑果汁，尾段有焦糖甜，适合搭配轻食。"),
        _note(users[0].id, "巴西黄波旁拼配", "巴西", "medium", ["坚果", "巧克力", "奶油"], 7, 5, 8, 7, "意式浓缩", recipes[2].id, "坚果和巧克力调稳定，牛奶融合度高，适合作为日常拿铁基底。"),
    ]


def _comments(users: list[User], notes: list[TastingNote]) -> list[Comment]:
    return [
        Comment(note_id=notes[0].id, user_id=users[0].id, content="这批次花魁确实不错，闷蒸时间可以再延长5秒试试，花香会更明显"),
        Comment(note_id=notes[0].id, user_id=users[2].id, content="请问豆子是哪家烘焙商的？想入手试试"),
        Comment(note_id=notes[2].id, user_id=users[1].id, content="不愧是瑰夏天花板！这个香气评分给10分一点不夸张"),
        Comment(note_id=notes[1].id, user_id=users[1].id, content="喜欢这种醇厚的口感，下午用法压壶来一壶真的很享受"),
    ]


def _likes(users: list[User], notes: list[TastingNote]) -> list[Like]:
    return [
        Like(user_id=users[0].id, note_id=notes[0].id),
        Like(user_id=users[2].id, note_id=notes[0].id),
        Like(user_id=users[1].id, note_id=notes[2].id),
        Like(user_id=users[2].id, note_id=notes[2].id),
        Like(user_id=users[1].id, note_id=notes[1].id),
    ]


def _follows(users: list[User]) -> list[UserFollow]:
    return [
        UserFollow(follower_id=users[1].id, following_id=users[0].id),
        UserFollow(follower_id=users[2].id, following_id=users[0].id),
        UserFollow(follower_id=users[1].id, following_id=users[2].id),
    ]


def _steps(names: list[str]) -> list[dict[str, int | str]]:
    return [{"step_number": index + 1, "description": name, "duration_seconds": 30 * (index + 1)} for index, name in enumerate(names)]


def _note(
    user_id: int,
    coffee_name: str,
    origin: str,
    roast_level: str,
    flavor_tags: list[str],
    aroma: int,
    acidity: int,
    body: int,
    overall: int,
    method: str,
    recipe_id: int | None,
    text: str,
) -> TastingNote:
    return TastingNote(
        user_id=user_id,
        coffee_name=coffee_name,
        origin=origin,
        roast_level=roast_level,
        flavor_tags=flavor_tags,
        aroma_score=aroma,
        acidity_score=acidity,
        body_score=body,
        overall_score=overall,
        brew_method=method,
        brew_recipe_id=recipe_id,
        notes_text=text,
    )
