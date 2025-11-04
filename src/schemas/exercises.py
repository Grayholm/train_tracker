from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


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

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v):
        if isinstance(v, str):
            v = v.lower().strip()

        try:
            return Category(v)
        except ValueError:
            available_categories = [e.value for e in Category]
            raise ValueError(
                f"Категория '{v}' не найдена. "
                f"Доступные категории: {', '.join(available_categories)}"
            )


class Exercise(ExerciseAdd):
    id: int


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None
