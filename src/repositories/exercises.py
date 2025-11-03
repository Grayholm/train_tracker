from src.models.exercises import ExercisesModel
from src.repositories.base import BaseRepository


class ExercisesRepository(BaseRepository):
    model = ExercisesModel
    mapper = ExerciseDataMapper