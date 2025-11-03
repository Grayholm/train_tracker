from datetime import date
from typing import List

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
