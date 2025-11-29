from unittest.mock import Mock, AsyncMock, patch

import jwt
import pytest
from fastapi import HTTPException
from itsdangerous import BadSignature
from sqlalchemy.exc import NoResultFound

from src.core.config import settings
from src.exceptions import ObjectAlreadyExistsException, ObjectNotFoundException, EmailIsAlreadyRegisteredException, LoginErrorException
from src.schemas.users import UserRequest, Roles
from src.services.auth import AuthService
from tests.base_test import BaseTestService


class TestAuthService(BaseTestService):

    def setup_method(self):
        super().setup_method()
        self.service = AuthService(db=self.mock_db, serializer=self.mock_serializer)

    def test_create_access_token_returns_token(self):
        secret_value = "mysecret"
        data = {
            "user_id": 123,
            "user_email": "test@example.com",
            "user_hashed_password": "mysecret",
            "user_role": Roles.USER.value,
        }

        with patch("src.core.config.settings.JWT_SECRET_KEY.get_secret_value", return_value=secret_value):
            token = self.service.create_access_token(data)

        assert isinstance(token, str)

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

        with patch("src.services.auth.jwt.decode", side_effect=jwt.exceptions.InvalidSignatureError):
            with pytest.raises(HTTPException) as exc_info:
                self.service.decode_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert "Неверная подпись" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_register_user_success(self):
        data = UserRequest(email="test@example.com", password="123456")

        with patch("src.core.tasks.send_confirmation_email.delay") as mock_email_delay:
            result = await self.service.register_user(data)

        self.mock_db.users.add.assert_called_once()

        self.mock_db.commit.assert_called_once()

        self.mock_serializer.dumps.assert_called_once_with("test@example.com")

        mock_email_delay.assert_called_once_with(
            to_email="test@example.com",
            token="TOK123",
        )

        assert "успешно" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self):

        self.mock_db.users.add.side_effect = ObjectAlreadyExistsException

        data = UserRequest(email="test@example.com", password="123456")

        with pytest.raises(EmailIsAlreadyRegisteredException):
            await self.service.register_user(data)

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

        self.mock_db.users.get_one = AsyncMock(return_value=fake_user)

        self.mock_db.users.login_is_active = AsyncMock()

        data = UserRequest(email="test@example.com", password=password)

        token = await self.service.login_and_get_access_token(data)

        self.mock_db.users.get_one.assert_called_once_with(email="test@example.com")
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_login_and_get_access_token_failure(self):
        self.mock_db.users.get_one = AsyncMock(side_effect=NoResultFound)

        data = UserRequest(email="fake@example.com", password="123456")

        with pytest.raises(LoginErrorException):
            await self.service.login_and_get_access_token(data)

        self.mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_login_with_wrong_password_raises_exception(self):
        correct_password = "correct123"
        hashed_password = self.service.hash_password(correct_password)

        fake_user = Mock(
            id=1,
            email="test@example.com",
            hashed_password=hashed_password,
            role=Mock(value="user"),
        )

        self.mock_db.users.get_one = AsyncMock(return_value=fake_user)

        data = UserRequest(email="test@example.com", password="wrongpassword")

        with pytest.raises(LoginErrorException):
            await self.service.login_and_get_access_token(data)

        self.mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_one_or_none_user_success(self):
        correct_password = "correct123"
        hashed_password = self.service.hash_password(correct_password)

        fake_user = Mock(
            id=1,
            email="test@example.com",
            hashed_password=hashed_password,
            role=Roles.USER.value,
        )

        self.service.get_one_or_none_user = AsyncMock(return_value=fake_user)

        user = await self.service.get_one_or_none_user(user_id=1)

        self.service.get_one_or_none_user.assert_called_once()
        assert user.id == 1
        assert user.hashed_password == hashed_password
        assert user.role == Roles.USER.value
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_one_or_none_user_failure(self):
        self.service.get_one_or_none_user = AsyncMock(return_value=None)
        user = await self.service.get_one_or_none_user(user_id=1)
        self.service.get_one_or_none_user.assert_called_once()
        assert user is None

    @pytest.mark.asyncio
    async def test_logout_success(self):
        await self.service.logout(user_id=1)

        self.mock_db.users.logout_is_active.assert_called_once_with(user_id=1)
        self.mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_user_success(self):
        token = "tok123"
        email = "test@example.com"

        self.mock_serializer.loads.return_value = email

        await self.service.confirm_user(token)

        self.mock_serializer.loads.assert_called_once_with(token, max_age=3600)
        self.mock_db.users.confirm_user.assert_called_once_with(email=email)
        self.mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_user_bad_signature(self):
        token = "badtoken"

        self.mock_serializer.loads.side_effect = BadSignature("badtoken")

        with pytest.raises(BadSignature):
            await self.service.confirm_user(token)

        assert not self.mock_db.users.confirm_user.called
        assert not self.mock_db.commit.called

    @pytest.mark.asyncio
    async def test_change_email_success(self):
        old_email = "oldemail@example.com"
        new_email = "newemail@example.com"

        self.mock_db.users.get_one_or_none = AsyncMock(return_value=None)

        with patch("src.core.tasks.send_confirmation_email.delay") as mock_email_delay:
            await self.service.change_email(new_email, old_email)

        self.mock_db.users.get_one_or_none.assert_called_once_with(email=new_email)
        self.mock_serializer.dumps.assert_called_once_with(new_email)
        mock_email_delay.assert_called_once_with(
            to_email=new_email,
            token="TOK123"
        )
        self.mock_db.users.change_email.assert_called_once_with(new_email, old_email)
        self.mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_email_existing_user_failure(self):
        old_email = "oldemail@example.com"
        new_email = "newemail@example.com"
        fake_user = Mock(
            id=1,
            email="newemail@example.com",
            hashed_password="hashed_password",
            role=Roles.USER.value,
        )

        self.mock_db.users.get_one_or_none = AsyncMock(return_value=fake_user)
        with pytest.raises(ValueError):
            await self.service.change_email(new_email, old_email)

        self.mock_db.users.get_one_or_none.assert_called_once_with(email=new_email)

    @pytest.mark.asyncio
    async def test_change_email_old_email_failure(self):
        old_email = "oldemail@example.com"
        new_email = "oldemail@example.com"
        with pytest.raises(ValueError):
            await self.service.change_email(new_email, old_email)

    @pytest.mark.asyncio
    async def test_change_password_success(self):
        old_password = "oldpass123"
        new_password = "newpass123"

        users_hashed_password = self.service.hash_password(old_password)

        self.mock_db.users.change_password = AsyncMock(return_value=None)

        user_id = 10

        await self.service.change_password(
            old_password=old_password,
            new_password=new_password,
            users_hashed_password=users_hashed_password,
            user_id=user_id
        )

        self.mock_db.users.change_password.assert_called_once()
        called_hash, called_id = self.mock_db.users.change_password.call_args[0]

        assert called_id == user_id
        assert called_hash != users_hashed_password
        assert self.service.verify_password(new_password, called_hash) is True

        self.mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self):
        old_password = "oldpass123"
        wrong_password = "WRONGpass"
        new_password = "newpass123"

        users_hashed_password = self.service.hash_password(old_password)

        user_id = 10

        with pytest.raises(ValueError, match="Неверный текущий пароль"):
            await self.service.change_password(
                old_password=wrong_password,
                new_password=new_password,
                users_hashed_password=users_hashed_password,
                user_id=user_id
            )

        self.mock_db.users.change_password.assert_not_called()
        self.mock_db.commit.assert_not_called()
