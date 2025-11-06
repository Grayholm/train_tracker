import typing
from datetime import date

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.db import Base

if typing.TYPE_CHECKING:
    from src.models.exercises import ExercisesModel


class WorkoutsModel(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    date: Mapped[date]
    description: Mapped[str] = mapped_column(String(500))
    exercises: Mapped[list["ExercisesModel"]] = relationship(
        back_populates="workouts",
        secondary="workout_exercises",
        cascade="all, delete",
    )


class WorkoutExerciseModel(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE")  # ← каскадное удаление
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    sets: Mapped[int]
    reps: Mapped[int]
    weight: Mapped[float]
