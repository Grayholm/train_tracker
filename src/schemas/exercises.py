import uuid
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
    id: uuid.UUID


class ExerciseBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str | None):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Поле не может быть пустым или содержать только пробелы")
        return v

class ExerciseUpdatePatch(ExerciseBaseUpdate):
    pass

class ExerciseUpdatePut(ExerciseBaseUpdate):
    name: str
    description: str
    category: Category

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None