from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from src.core.db import Base


class ExerciseModel(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    # надо подумать, можно ли Enum класс использовать тут или просто str
    category: Mapped[str]