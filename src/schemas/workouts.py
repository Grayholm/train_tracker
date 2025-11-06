import datetime as dt
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, field_validator

from src.schemas.exercises import Exercise

#-------------------------------------
class ExerciseToAdd(BaseModel):
    id: int
    sets: int
    reps: int
    weight: float

class WorkoutRequest(BaseModel):
    date: dt.date
    description: str
    exercises: list[ExerciseToAdd]
#-------------------------------------

class WorkoutAdd(BaseModel):
    user_id: int
    date: dt.date
    description: str

class Workout(WorkoutAdd):
    id: int

class WorkoutBaseUpdate(BaseModel):
    date: dt.date = dt.date.today()
    description: Optional[str] = None
    exercises: Optional[List[Exercise]] = None

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
    user_id: int
    date: Optional[date] = None
    description: Optional[str] = None
    exercises: Optional[List[Exercise]] = None


class WorkoutExerciseAdd(BaseModel):
    workout_id: int
    exercise_id: int
    sets: int
    reps: int
    weight: float

class WorkoutExercise(WorkoutExerciseAdd):
    pass