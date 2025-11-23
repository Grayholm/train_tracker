import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, Field


class Category(Enum):
    CHEST = "chest"
    BACK = "back"
    LEGS = "legs"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    ABS = "abs"
    CARDIO = "cardio"
    STRETCHING = "stretching"

class ExerciseAddRequest(BaseModel):
    name: str
    description: Optional[str] = None

class ExerciseAdd(BaseModel):
    name: str
    description: Optional[str] = None
    category: Category


class Exercise(ExerciseAdd):
    id: int


class ExerciseBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

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
    description: str = Field(min_length=6)


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None