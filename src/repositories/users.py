from src.models.users import UsersModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper


class UsersRepository(BaseRepository):
    model = UsersModel
    mapper = UserDataMapper

