import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException
from itsdangerous import URLSafeTimedSerializer, BadSignature
from passlib.context import CryptContext
from pydantic import EmailStr

from src.core.config import settings
from src.core.db_manager import DBManager
from src.core.tasks import send_confirmation_email
from src.exceptions import (
    ObjectNotFoundException,
    EmailIsAlreadyRegisteredException,
    LoginErrorException,
)
from src.schemas.users import UserRequest, UserAdd, Roles, User
from src.services.base import BaseService


class AuthService(BaseService):
    def __init__(self, db: DBManager | None = None, serializer=None):
        super().__init__(db=db)
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        if serializer is not None:
            self.serializer = serializer
        else:
            self.serializer = URLSafeTimedSerializer(
                settings.secret_key.get_secret_value()
            )

    def create_access_token(self, data: dict) -> str:
        logging.debug("Create access token")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.JWT_SECRET_KEY.get_secret_value(),
                algorithm=settings.JWT_ALGORITHM,
            )
            return encoded_jwt
        except Exception as e:
            logging.error(f"Token creation failed: {e}")
            raise

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def decode_token(self, token: str) -> dict:
        logging.debug("Decode token")
        try:
            result = jwt.decode(
                token,
                settings.JWT_SECRET_KEY.get_secret_value(),
                algorithms=[settings.JWT_ALGORITHM],
            )
            logging.info("Token decoded")
            return result
        except jwt.exceptions.InvalidSignatureError:
            logging.error("Invalid token")
            raise HTTPException(status_code=401, detail="Ошибка: Неверная подпись(токен)")

    async def register_user(self, data: UserRequest):
        logging.info(f"Начинаем регистрацию пользователя с почтой: {data.email}")

        new_user = UserAdd(
            email=data.email, hashed_password=self.hash_password(data.password), role=Roles.USER
        )

        try:
            await self.db.users.add(new_user)
            await self.db.commit()
            logging.info(f"Пользователь успешно зарегистрировался с почтой={new_user.email}")
            confirmation_token = self.serializer.dumps(data.email)
            send_confirmation_email.delay(to_email=data.email, token=confirmation_token)
            return {
                "message": "Вы успешно зарегистрировались! Проверьте почту, чтобы подтвердить свою учетную запись"
            }
        except ObjectNotFoundException:
            logging.warning(f"Пользователь ввел уже существующую почту, {new_user.email}")
            raise EmailIsAlreadyRegisteredException

    async def login_and_get_access_token(self, data: UserRequest):
        logging.info(f"Login and get access token for email: {data.email}")
        try:
            user = await self.db.users.get_one(email=data.email)
        except ObjectNotFoundException:
            logging.warning(f"Неверная почта или пароль для пользователя {data.email}")
            raise LoginErrorException

        if not self.verify_password(data.password, user.hashed_password):
            logging.warning(f"Неверная почта или пароль для пользователя {data.email}")
            raise LoginErrorException

        await self.db.users.login_is_active(user.id)
        await self.db.commit()

        token = self.create_access_token(
            {
                "user_id": user.id,
                "user_email": user.email,
                "user_hashed_password": user.hashed_password,
                "user_role": user.role.value,
            }
        )

        logging.info(f"Login successful: {data.email}, user_id={user.id}")
        return token

    async def get_one_or_none_user(self, user_id: int) -> Optional[User]:
        return await self.db.users.get_one_or_none(id=user_id)

    async def logout(self, user_id: int):
        await self.db.users.logout_is_active(user_id=user_id)
        await self.db.commit()

    async def confirm_user(self, token: str) -> None:
        try:
            email = self.serializer.loads(token, max_age=3600)
        except BadSignature:
            raise

        await self.db.users.confirm_user(email=email)
        await self.db.commit()

    async def change_email(self, new_email: str, old_email: EmailStr):
        if new_email == old_email:
            raise ValueError("Новый email совпадает с текущим")

        existing_user = await self.db.users.get_one_or_none(email=new_email)
        if existing_user:
            raise ValueError("Этот email уже используется другим пользователем")

        confirmation_token = self.serializer.dumps(new_email)

        send_confirmation_email.delay(to_email=new_email, token=confirmation_token)

        await self.db.users.change_email(new_email, old_email)
        await self.db.commit()

    async def change_password(
        self, old_password: str, new_password: str, users_hashed_password: str, user_id: int
    ):
        if not self.verify_password(old_password, users_hashed_password):
            raise ValueError("Неверный текущий пароль")

        password = self.hash_password(new_password)
        await self.db.users.change_password(password, user_id)
        await self.db.commit()
