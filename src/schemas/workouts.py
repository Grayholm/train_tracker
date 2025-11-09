import datetime as dt
import uuid
from typing import List, Optional

from pydantic import BaseModel, field_validator

#-------------------------------------
class ExerciseToAdd(BaseModel):
    id: uuid.UUID
    sets: int
    reps: int
    weight: float

class WorkoutRequest(BaseModel):
    date: dt.date = dt.date.today()
    description: str
    exercises: list[ExerciseToAdd]
#-------------------------------------

class WorkoutAdd(BaseModel):
    user_id: uuid.UUID
    date: dt.date
    description: str

class Workout(WorkoutAdd):
    id: uuid.UUID

class WorkoutBaseUpdate(BaseModel):
    date: dt.date = dt.date.today()
    description: Optional[str] = None
    exercises: Optional[List[ExerciseToAdd]] = None

    @field_validator("description")
    @classmethod
    def not_empty(cls, v: str | None):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Поле не может быть пустым или содержать только пробелы")
        return v

class WorkoutUpdatePatch(WorkoutBaseUpdate):
    pass

class WorkoutUpdate(BaseModel):
    user_id: uuid.UUID
    date: Optional[dt.date] = None
    description: Optional[str] = None


class WorkoutExerciseAdd(BaseModel):
    workout_id: uuid.UUID
    exercise_id: uuid.UUID
    sets: int
    reps: int
    weight: float

class WorkoutExercise(WorkoutExerciseAdd):
    pass