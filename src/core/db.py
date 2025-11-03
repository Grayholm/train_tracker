from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.core.config import settings
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Создаем синхронный движок для Celery
sync_engine = create_engine(settings.db_url.replace("asyncpg", "psycopg2"))
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

db_params = {}
if settings.MODE == "TEST":
    db_params = {"poolclass": NullPool}

engine = create_async_engine(settings.db_url, echo=True, **db_params)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null_pool = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
