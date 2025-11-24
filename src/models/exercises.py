import typing

from sqlalchemy import String, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.db import Base
from src.models.mixins.id_mixins import IDMixin
from src.models.mixins.timestamp_mixins import TimestampsMixin
from src.schemas.exercises import Category

if typing.TYPE_CHECKING:
    from src.models.workouts import WorkoutsModel


class ExercisesModel(IDMixin, TimestampsMixin, Base):
    __tablename__ = "exercises"

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    category: Mapped[Category] = mapped_column(Enum(Category))

    workouts: Mapped[list["WorkoutsModel"]] = relationship(
        back_populates="exercises",
        secondary="workout_exercises",
    )
