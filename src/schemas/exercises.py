from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Category(Enum):
    CHEST = "chest"
    BACK = "back"
    LEGS = "legs"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    ABS = "abs"
    CARDIO = "cardio"
    STRETCHING = "stretching"

class ExerciseAdd(BaseModel):
    name: str
    description: Optional[str] = None
    category: Category

class Exercise(ExerciseAdd):
    id: int