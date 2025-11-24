from pydantic import EmailStr
from sqlalchemy import update

from src.models.users import UsersModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper


class UsersRepository(BaseRepository):
    model = UsersModel
    mapper = UserDataMapper

    async def confirm_user(self, email: str) -> None:
        query = (
            update(self.model)
            .where(self.model.email == email)
            .values(is_verified=True, is_active=True)
        )
        await self.session.execute(query)

    async def change_email(self, new_email: str, user_email: EmailStr) -> None:
        query = (
            update(self.model)
            .where(self.model.email == user_email)
            .values(email=new_email, is_verified=False)
        )
        await self.session.execute(query)

    async def change_password(self, new_password: str, user_id: int) -> None:
        query = (
            update(self.model).where(self.model.id == user_id).values(hashed_password=new_password)
        )
        await self.session.execute(query)

    async def logout_is_active(self, user_id: int):
        query = update(self.model).where(self.model.id == user_id).values(is_active=False)
        await self.session.execute(query)

    async def login_is_active(self, user_id: int):
        query = update(self.model).where(self.model.id == user_id).values(is_active=True)
        await self.session.execute(query)
