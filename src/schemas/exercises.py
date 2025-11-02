from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Category(Enum):
    pass

class ExerciseAdd(BaseModel):
    name: str
    description: Optional[str] = None
    category: Category = Category.name

class Exercise(ExerciseAdd):
    id: int