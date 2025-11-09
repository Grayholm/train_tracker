from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.models.mixins.id_mixins import IDMixin
from src.models.mixins.timestamp_mixins import TimestampsMixin
from src.schemas.users import Roles


class UsersModel(IDMixin, TimestampsMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Roles] = mapped_column(Enum(Roles))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
