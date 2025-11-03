from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.schemas.users import Roles


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[Roles] = mapped_column(Enum(Roles))