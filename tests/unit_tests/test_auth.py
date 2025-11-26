from unittest.mock import Mock, AsyncMock, patch

import jwt
import pytest
from fastapi import HTTPException

from src.core.config import settings
from src.exceptions import ObjectNotFoundException, EmailIsAlreadyRegisteredException
from src.schemas.users import UserRequest, Roles
from src.services.auth import AuthService


class TestAuthService:
    mock_db: Mock

    def setup_method(self):
        self.mock_db = Mock()
        self.mock_db.users = AsyncMock()
        self.mock_db.commit = AsyncMock()

        self.mock_serializer = Mock()
        self.mock_serializer.dumps.return_value = "TOK123"

        self.service = AuthService(db=self.mock_db, serializer=self.mock_serializer)

    def test_create_access_token_returns_token(self):
        secret_value = "mysecret"
        data = {
            "user_id": 123,
            "user_email": "test@example.com",
            "user_hashed_password": "mysecret",
            "user_role": Roles.USER.value,
        }

        # Мокаем settings.JWT_SECRET_KEY.get_secret_value()
        with patch("src.core.config.settings.JWT_SECRET_KEY.get_secret_value", return_value=secret_value):
            token = self.service.create_access_token(data)

        # Assert
        assert isinstance(token, str)

        # Декодируем токен, чтобы проверить содержимое
        decoded = jwt.decode(token, secret_value, algorithms=[settings.JWT_ALGORITHM])

        assert decoded["user_id"] == 123
        assert decoded["user_email"] == "test@example.com"
        assert decoded["user_hashed_password"] == "mysecret"
        assert decoded["user_role"] == Roles.USER.value
        assert "exp" in decoded

    def test_create_access_token_raises_exception(self):
        data = {
            "user_id": 123,
            "user_email": "test@example.com",
            "user_hashed_password": "mysecret",
            "user_role": Roles.USER.value,
        }

        with patch("src.core.config.settings.JWT_SECRET_KEY.get_secret_value", return_value="secret"), \
                patch("src.services.auth.jwt.encode", side_effect=Exception("fail")):
            with pytest.raises(Exception) as exc_info:
                self.service.create_access_token(data)

        assert "fail" in str(exc_info.value)

    def test_hash_and_verify_password(self):
        password = "mysecret"
        hashed = self.service.hash_password(password)

        assert self.service.verify_password(password, hashed) is True
        assert self.service.verify_password("wrongpass", hashed) is False

    def test_decode_token_success(self):
        data = {
            "user_id": 123,
            "user_email": "test@example.com",
            "user_hashed_password": "mysecret",
            "user_role": Roles.USER.value,
        }

        with patch("src.core.config.settings.JWT_SECRET_KEY.get_secret_value", return_value="mysecret"):
            token = self.service.create_access_token(data)
            decoded = self.service.decode_token(token)

        assert isinstance(decoded, dict)
        assert decoded["user_id"] == 123
        assert decoded["user_email"] == "test@example.com"
        assert decoded["user_hashed_password"] == "mysecret"
        assert decoded["user_role"] == Roles.USER.value
        assert "exp" in decoded

    def test_decode_token_fail(self):
        invalid_token = "invalid.token.string"

        # Мокаем секрет и заставляем jwt.decode выбросить ошибку подписи
        with patch("src.services.auth.jwt.decode", side_effect=jwt.exceptions.InvalidSignatureError):
            with pytest.raises(HTTPException) as exc_info:
                self.service.decode_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert "Неверная подпись" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_register_user_success(self):
        # self.mock_db.users.add = AsyncMock()

        # Input
        data = UserRequest(email="test@example.com", password="123456")

        # Мокаем отправку письма
        with patch("src.core.tasks.send_confirmation_email.delay") as mock_email_delay:
            # Act
            result = await self.service.register_user(data)

        # --- Assert ---

        # Проверяем, что user добавлен в БД
        self.mock_db.users.add.assert_called_once()

        # commit вызван
        self.mock_db.commit.assert_called_once()

        # Токен сериализован корректно
        self.mock_serializer.dumps.assert_called_once_with("test@example.com")

        # Отправка письма была вызвана
        mock_email_delay.assert_called_once_with(
            to_email="test@example.com",
            token="TOK123",
        )

        # Ответ сервиса корректный
        assert "успешно" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self):

        # Имитируем ошибку в add()
        self.mock_db.users.add.side_effect = ObjectNotFoundException

        data = UserRequest(email="test@example.com", password="123456")

        with pytest.raises(EmailIsAlreadyRegisteredException):
            await self.service.register_user(data)

        # commit вызываться НЕ должен
        self.mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_login_and_get_access_token_success(self):
        # Arrange
        password = "123456"
        hashed_password = self.service.hash_password(password)  # настоящий хэш

        fake_user = Mock()
        fake_user.id = 1
        fake_user.email = "test@example.com"
        fake_user.hashed_password = hashed_password
        fake_user.role = Mock(value="user")

        # Мокаем метод получения пользователя
        self.mock_db.users.get_one = AsyncMock(return_value=fake_user)

        # Мокаем login_is_active и commit
        self.mock_db.users.login_is_active = AsyncMock()
        self.mock_db.commit = AsyncMock()

        data = UserRequest(email="test@example.com", password=password)

        # Act
        token = await self.service.login_and_get_access_token(data)

        # Assert
        self.mock_db.users.get_one.assert_called_once_with(email="test@example.com")
        assert isinstance(token, str)