from src.models.exercises import ExercisesModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ExerciseDataMapper


class ExercisesRepository(BaseRepository):
    model = ExercisesModel
    mapper = ExerciseDataMapper
