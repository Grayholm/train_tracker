from sqlalchemy.exc import NoResultFound

from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
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

    async def add_exercise(self, exercise_example: ExerciseAdd):
        name = exercise_example.name.capitalize()
        exercise = ExerciseAdd(
            name=name,
            description=exercise_example.description,
            category=exercise_example.category,
        )
        obj1 = await self.db.exercises.get_one_or_none(name=exercise.name)
        if obj1:
            raise ObjectAlreadyExistsException
        created = await self.db.exercises.add(exercise)
        await self.db.commit()
        return created

    async def delete_exercise(self, exercise_id: int):
        try:
            await self.db.exercises.delete(id=exercise_id)
            await self.db.commit()
        except ObjectNotFoundException:
            raise
