import typing
import uuid
from datetime import date

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.db import Base
from src.models.mixins.id_mixins import IDMixin
from src.models.mixins.timestamp_mixins import TimestampsMixin

if typing.TYPE_CHECKING:
    from src.models.exercises import ExercisesModel


class WorkoutsModel(IDMixin, TimestampsMixin, Base):
    __tablename__ = "workouts"

    user_id: Mapped[uuid.UUID] = mapped_column(Integer, ForeignKey("users.id"))
    date: Mapped[date]
    description: Mapped[str] = mapped_column(String(500))
    exercises: Mapped[list["ExercisesModel"]] = relationship(
        back_populates="workouts",
        secondary="workout_exercises",
        cascade="all, delete",
    )


class WorkoutExerciseModel(IDMixin, TimestampsMixin, Base):
    __tablename__ = "workout_exercises"

    workout_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE")  # ← каскадное удаление
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercises.id"))
    sets: Mapped[int]
    reps: Mapped[int]
    weight: Mapped[float]
