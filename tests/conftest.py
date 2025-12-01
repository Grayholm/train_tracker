#type: noqa: F401

from unittest.mock import patch
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update

from src.core.db_manager import DBManager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from src.main import app
from src.core.config import settings
from src.core.db import Base, engine, async_session_maker
from src.models import (
    ExercisesModel,
    WorkoutsModel,
    WorkoutExerciseModel,
    UsersModel,
)
from src.schemas.users import Roles


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "TEST"

@pytest.fixture
async def patch_celery_delay():
    with patch("src.services.auth.send_confirmation_email.delay") as mock_delay:
        mock_delay.return_value = None
        yield mock_delay

@pytest.fixture()
async def db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(scope="session")
async def ac():
    # Инициализируем кэширующий бэкенд для тестов до создания клиента
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="session")
async def authenticated_ac(ac):
    """Возвращает залогиненного USER клиента"""
    email = "testuser@example.com"
    password = "testpassword123"
    with patch("src.services.auth.send_confirmation_email.delay") as mock_delay:
        mock_delay.return_value = None
        await ac.post("/auth/register", json={"email": email, "password": password})
    
    response = await ac.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert ac.cookies.get("access_token") is not None
    
    return ac

@pytest.fixture(scope="session")
async def admin_ac(ac):
    """Возвращает залогиненного ADMIN клиента"""
    email = "admin@example.com"
    password = "adminpass123"
    with patch("src.services.auth.send_confirmation_email.delay") as mock_delay:
        mock_delay.return_value = None
        await ac.post("/auth/register", json={"email": email, "password": password})
    
    # Меняем роль в БД
    async with DBManager(session_factory=async_session_maker) as db:
        stmt = update(UsersModel).where(UsersModel.email == email).values(role=Roles.ADMIN)
        await db.session.execute(stmt)
        await db.session.commit()
    
    # Теперь логинимся с админской ролью
    response = await ac.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert ac.cookies.get("access_token") is not None
    
    return ac