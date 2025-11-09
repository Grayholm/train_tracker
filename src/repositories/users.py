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