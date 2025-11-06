from sqlalchemy.exc import NoResultFound

from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException, DataIsEmptyException
from src.schemas.exercises import ExerciseAdd, ExerciseUpdate, ExerciseUpdatePut, ExerciseUpdatePatch
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

    async def update_exercise(self, exercise_id: int, exercise: ExerciseUpdatePut):
        data_dict = exercise.model_dump(exclude_unset=True) if exercise else {}
        if not data_dict:
            return DataIsEmptyException("Отсутствуют данные для обновления")
        try:
            await self.get_exercise(exercise_id)
        except ObjectNotFoundException:
            raise

        data = ExerciseUpdate(**data_dict)

        result = await self.db.exercises.update(data, id=exercise_id)
        await self.db.commit()
        return result

    async def partially_update_exercise(self, exercise_id: int, exercise: ExerciseUpdatePatch):
        data_dict = exercise.model_dump(exclude_unset=True) if exercise else {}
        if not data_dict:
            return DataIsEmptyException("Отсутствуют данные для обновления")
        try:
            await self.get_exercise(exercise_id)
        except ObjectNotFoundException:
            raise

        data = ExerciseUpdate(**data_dict)

        result = await self.db.exercises.update(data, id=exercise_id)
        await self.db.commit()
        return result