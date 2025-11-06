from src.models.exercises import ExercisesModel
from src.models.users import UsersModel
from src.models.workouts import WorkoutsModel, WorkoutExerciseModel
from src.repositories.mappers.base import DataMapper
from src.schemas.exercises import Exercise
from src.schemas.users import User
from src.schemas.workouts import Workout, WorkoutExercise


class UserDataMapper(DataMapper):
    db_model = UsersModel
    schema = User


class ExerciseDataMapper(DataMapper):
    db_model = ExercisesModel
    schema = Exercise


class WorkoutDataMapper(DataMapper):
    db_model = WorkoutsModel
    schema = Workout

class WorkoutExerciseDataMapper(DataMapper):
    db_model = WorkoutExerciseModel
    schema = WorkoutExercise