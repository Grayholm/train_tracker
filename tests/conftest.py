#type: noqa: F401

from unittest.mock import patch
import pytest
from httpx import ASGITransport, AsyncClient

from src.core.db_manager import DBManager
from src.main import app
from src.core.config import settings
from src.core.db import Base, engine, async_session_maker
from src.models import (
    ExercisesModel,
    WorkoutsModel,
    WorkoutExerciseModel,
    UsersModel,
)


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "TEST"

@pytest.fixture()
async def db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

@pytest.fixture()
def patch_celery_delay():
    with patch("src.services.auth.send_confirmation_email.delay") as mock_delay:
        mock_delay.return_value = None
        yield mock_delay

@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture()
async def authenticated_ac(ac, patch_celery_delay):
    """Возвращает залогиненного клиента с установленным access_token"""
    # Регистрируемся
    email = "testuser@example.com"
    password = "testpassword123"
    
    await ac.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    
    # Логинимся
    response = await ac.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    
    assert response.status_code == 200
    assert ac.cookies.get("access_token") is not None
    assert ac.cookies["access_token"] == response.json()["access_token"]
    
    return ac