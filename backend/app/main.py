import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.database import AsyncSessionLocal, Base, engine
from app.middlewares.auth import auth_middleware
from app.middlewares.error_handler import register_exception_handlers
from app.middlewares.logger import logger_middleware
from app.routes import auth, bean, comment, note, recipe, user
from app.utils.seed_data import seed_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_database(session)
    yield


app = FastAPI(title="咖啡品鉴社区 API", version="1.0.0", lifespan=lifespan)
settings = get_settings()

app.middleware("http")(logger_middleware)
app.middleware("http")(auth_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(note.router)
app.include_router(bean.router)
app.include_router(recipe.router)
app.include_router(comment.router)


@app.get("/api/health")
async def health():
    return {"code": 0, "message": "success", "data": {"status": "ok"}}

