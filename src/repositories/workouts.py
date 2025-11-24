from src.models.workouts import WorkoutsModel, WorkoutExerciseModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import WorkoutDataMapper, WorkoutExerciseDataMapper


class WorkoutsRepository(BaseRepository):
    model = WorkoutsModel
    mapper = WorkoutDataMapper


class WorkoutExerciseRepository(BaseRepository):
    model = WorkoutExerciseModel
    mapper = WorkoutExerciseDataMapper
