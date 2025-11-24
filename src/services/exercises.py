from sqlalchemy.exc import NoResultFound, IntegrityError

from src.exceptions import (
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
    DataIsEmptyException,
)
from src.schemas.exercises import ExerciseAdd, ExerciseUpdate, Category
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

    async def add_exercise(self, exercise_example: dict):
        name = exercise_example["name"].capitalize()
        exercise = ExerciseAdd(
            name=name,
            description=exercise_example["description"],
            category=exercise_example["category"],
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

    async def update_exercise(self, exercise_id: int, data_dict: dict, category: Category):
        if not data_dict:
            raise DataIsEmptyException("Отсутствуют данные для обновления")

        try:
            await self.get_exercise(exercise_id)
        except ObjectNotFoundException:
            raise

        data_dict["category"] = category
        data = ExerciseUpdate(**data_dict)

        try:
            result = await self.db.exercises.update(data, id=exercise_id)
            await self.db.commit()
            return result
        except IntegrityError:
            raise DataIsEmptyException("Название для упражнения не должно быть пустым")

    async def partially_update_exercise(
        self, exercise_id: int, data_dict: dict, category: Category
    ):
        if category is not None:
            data_dict["category"] = category

        if not data_dict:
            raise DataIsEmptyException("Отсутствуют данные для обновления")

        try:
            await self.get_exercise(exercise_id)
        except ObjectNotFoundException:
            raise

        data = ExerciseUpdate(**data_dict)

        result = await self.db.exercises.update(data, id=exercise_id)
        await self.db.commit()
        return result
