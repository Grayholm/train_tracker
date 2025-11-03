from src.models.workouts import WorkoutsModel
from src.repositories.base import BaseRepository


class WorkoutsRepository(BaseRepository):
    model = WorkoutsModel
    mapper = WorkoutDataMapper