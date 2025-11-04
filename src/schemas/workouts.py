from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from src.schemas.exercises import Exercise


class WorkoutRequest(BaseModel):
    date: date
    description: str
    exercises: List[Exercise]


class WorkoutAdd(WorkoutRequest):
    user_id: int


class Workout(WorkoutAdd):
    id: int


class WorkoutUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    exercises: Optional[List[Exercise]] = None
