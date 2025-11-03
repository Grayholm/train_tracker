from src.models.workouts import WorkoutsModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import WorkoutDataMapper


class WorkoutsRepository(BaseRepository):
    model = WorkoutsModel
    mapper = WorkoutDataMapper