import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, field_validator, Field


#-------------------------------------
class ExerciseToAdd(BaseModel):
    id: int
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float = Field(gt=0)

class WorkoutRequest(BaseModel):
    date: dt.date = dt.date.today()
    description: Optional[str] = None
    exercises: list[ExerciseToAdd]
#-------------------------------------

class WorkoutAdd(BaseModel):
    user_id: int
    date: dt.date
    description: Optional[str] = None

class Workout(WorkoutAdd):
    id: int

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
    user_id: int
    date: Optional[dt.date] = None
    description: Optional[str] = None


class WorkoutExerciseAdd(BaseModel):
    workout_id: int
    exercise_id: int
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float = Field(gt=0)

class WorkoutExercise(WorkoutExerciseAdd):
    pass

class WorkoutToResponse(Workout):
    exercises: list[WorkoutExercise]