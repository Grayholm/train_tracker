import typing

from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.db import Base
from src.schemas.exercises import Category

if typing.TYPE_CHECKING:
    from src.models.workouts import WorkoutsModel


class ExercisesModel(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    category: Mapped[Category] = mapped_column(Enum(Category))

    workouts: Mapped[list["WorkoutsModel"]] = relationship(
        back_populates="exercises",
        secondary="workout_exercises",
    )
