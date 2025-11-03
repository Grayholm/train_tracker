from sqlalchemy.exc import NoResultFound

from src.exceptions import ObjectNotFoundException
from src.schemas.exercises import ExerciseAdd
from src.services.base import BaseService


class ExercisesService(BaseService):
    async def get_exercises(self):
        exercises = await self.db.exercises.get_all()
        return exercises

    async def get_exercise(self, exercise_id):
        try:
            exercise = await self.db.exercises.get_one(id=exercise_id)
            return exercise
        except NoResultFound:
            raise ObjectNotFoundException

    async def add_exercise(self, exercise: ExerciseAdd):
        return await self.db.exercises.add(exercise)
