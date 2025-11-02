import typing
from datetime import date

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.db import Base

if typing.TYPE_CHECKING:
    from src.models.exercises import ExerciseModel


class WorkoutModel(Base):
    __tablename__ = 'workouts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date]
    description: Mapped[str] = mapped_column(String(500))
    exercises: Mapped[list["ExerciseModel"]] = relationship(
        back_populates="workouts",
        secondary="workout_exercises",
    )

class WorkoutExerciseModel(Base):
    __tablename__ = 'workout_exercises'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))