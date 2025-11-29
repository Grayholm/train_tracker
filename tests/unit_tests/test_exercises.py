from unittest.mock import Mock, AsyncMock

import pytest
from sqlalchemy.exc import NoResultFound

from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException, DataIsEmptyException
from src.schemas.exercises import Category, Exercise, ExerciseUpdate
from src.services.exercises import ExercisesService
from tests.base_test import BaseTestService


class TestExercisesService(BaseTestService):
    service_name = ExercisesService

    def setup_method(self):
        super().setup_method()
        self.service = ExercisesService(db=self.mock_db)

    @pytest.mark.asyncio
    async def test_get_exercises_success(self):
        self.mock_db.exercises.get_all = AsyncMock(return_value=[])
        exercises = await self.service.get_exercises()
        assert exercises == []
        self.mock_db.exercises.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_exercise_success(self):
        exercise_example = Mock(
            id=1,
            name="Жим лежа",
            description="Базовое упражнение",
            category="chest",
        )
        self.mock_db.exercises.get_one = AsyncMock(return_value=exercise_example)
        exercise = await self.service.get_exercise(1)
        assert exercise == exercise
        self.mock_db.exercises.get_one.assert_called_once_with(id=1)

    @pytest.mark.asyncio
    async def test_get_exercise_failure(self):
        self.mock_db.exercises.get_one.side_effect = NoResultFound

        with pytest.raises(ObjectNotFoundException):
            await self.service.get_exercise(1)

        self.mock_db.exercises.get_one.assert_called_once_with(id=1)

    @pytest.mark.asyncio
    async def test_add_exercise_success(self):
        # Arrange
        exercise_example = {
            "name":"Жим лежа",
            "description":"Базовое упражнение",
            "category":"chest",
        }
        exercise_example_to_response = Exercise(
            id=1,
            name="Жим лежа",
            description="Базовое упражнение",
            category=Category.CHEST,
        )
        self.mock_db.exercises.get_one_or_none = AsyncMock(return_value=None)
        self.mock_db.exercises.add = AsyncMock(return_value=exercise_example_to_response)

        # Act
        exercise = await self.service.add_exercise(exercise_example)

        # Assert
        self.mock_db.exercises.get_one_or_none.assert_called_once_with(name="Жим лежа")
        self.mock_db.exercises.add.assert_called_once()
        called_arg = self.mock_db.exercises.add.call_args[0][0]
        assert called_arg.name == "Жим лежа"
        assert called_arg.description == "Базовое упражнение"
        assert called_arg.category == Category.CHEST
        self.mock_db.commit.assert_called_once()
        assert exercise.name == "Жим лежа"
        assert exercise.description == "Базовое упражнение"
        assert exercise.category == Category.CHEST

    @pytest.mark.asyncio
    async def test_add_exercise_failure(self):
        # Arrange
        exercise_example = {
            "name":"Жим лежа",
            "description":"Базовое упражнение",
            "category":"chest",
        }
        existing_obj = Exercise(
            id=1,
            name="Жим лежа",
            description="Базовое упражнение",
            category=Category.CHEST,
        )
        self.mock_db.exercises.get_one_or_none = AsyncMock(return_value=existing_obj)

        # Act
        with pytest.raises(ObjectAlreadyExistsException):
            await self.service.add_exercise(exercise_example)

        # Assert
        self.mock_db.exercises.add.assert_not_called()
        self.mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_exercise_success(self):
        self.mock_db.exercises.delete = AsyncMock(return_value=True)
        await self.service.delete_exercise(1)
        self.mock_db.exercises.delete.assert_called_once()
        self.mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_exercise_failure(self):
        self.mock_db.exercises.delete.side_effect = ObjectNotFoundException
        with pytest.raises(ObjectNotFoundException):
            await self.service.delete_exercise(1)
        self.mock_db.exercises.delete.assert_called_once_with(id=1)
        self.mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_exercise_success(self):
        # Arrange
        exercise_id = 1
        existing_obj = Exercise(
            id=1,
            name="Жим лежа",
            description="Базовое упражнение",
            category=Category.CHEST,
        )
        existing_obj_new = Exercise(
            id=1,
            name="Подтягивания",
            description="Базовое упражнение на спину",
            category=Category.BACK,
        )
        exercise_example = {
            "name": "Подтягивания",
            "description": "Базовое упражнение на спину"
        }
        category = Category.BACK
        self.service.get_exercise = AsyncMock(return_value=existing_obj)
        self.mock_db.exercises.update = AsyncMock(return_value=existing_obj_new)

        # Act
        exercise = await self.service.update_exercise(exercise_id, exercise_example, category)

        # Assert
        self.service.get_exercise.assert_called_once_with(exercise_id)
        called_arg = self.mock_db.exercises.update.call_args[0][0]
        assert called_arg.name == "Подтягивания"
        assert called_arg.description == "Базовое упражнение на спину"
        assert called_arg.category == category
        self.mock_db.commit.assert_called_once()
        assert exercise.name == "Подтягивания"
        assert exercise.description == "Базовое упражнение на спину"
        assert exercise.category == category

    @pytest.mark.parametrize("name, description", [
        ("Подтягивания", None),
        (None, "Базовое упражнение на спину"),
        (None, None)
    ])
    @pytest.mark.asyncio
    async def test_update_exercise_data_is_empty_failure(self, name, description):
        # Arrange
        exercise_id = 1
        exercise_example = {
            "name": name,
            "description": description
        }
        category = Category.BACK
        self.service.get_exercise = AsyncMock()
        self.mock_db.exercises.update = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act + Assert
        with pytest.raises(DataIsEmptyException, match="Поле name или description пусто"):
            await self.service.update_exercise(exercise_id, exercise_example, category)

        self.service.get_exercise.assert_not_called()
        self.mock_db.exercises.update.assert_not_called()
        self.mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_exercise_obj_not_found_failure(self):
        # Arrange
        exercise_id = 1
        exercise_example = {
            "name": "Подтягивания",
            "description": "Базовое упражнение на спину"
        }
        category = Category.BACK
        self.service.get_exercise = AsyncMock(side_effect=ObjectNotFoundException)
        self.mock_db.exercises.update = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act + Assert
        with pytest.raises(ObjectNotFoundException):
            await self.service.update_exercise(exercise_id, exercise_example, category)

        # Assert
        self.service.get_exercise.assert_called_once_with(exercise_id)
        self.mock_db.exercises.update.assert_not_called()
        self.mock_db.commit.assert_not_called()

    @pytest.mark.parametrize("name, description", [
        ("Подтягивания", "Базовое упражнение на спину"),
        ("Подтягивания", None),
    ])
    @pytest.mark.asyncio
    async def test_partially_update_exercise_success(self, name, description):
        # Arrange
        exercise_id = 1
        existing_obj = Exercise(
            id=1,
            name="Жим лежа",
            description="Базовое упражнение",
            category=Category.CHEST,
        )
        existing_obj_new = Exercise(
            id=1,
            name=name,
            description=description,
            category=Category.BACK,
        )
        exercise_example = {
            "name": name,
            "description": description
        }
        self.service.get_exercise = AsyncMock(return_value=existing_obj)
        self.mock_db.exercises.update = AsyncMock(return_value=existing_obj_new)
        self.mock_db.commit = AsyncMock()

        # Act
        exercise = await self.service.partially_update_exercise(exercise_id, exercise_example, Category.BACK)

        # Assert
        self.service.get_exercise.assert_called_once_with(exercise_id)
        called_arg = self.mock_db.exercises.update.call_args[0][0]
        assert called_arg.name == name
        assert called_arg.description == description
        assert called_arg.category == Category.BACK
        self.mock_db.commit.assert_called_once()
        assert exercise.name == name
        assert exercise.description == description
        assert exercise.category == Category.BACK

    @pytest.mark.asyncio
    async def test_partially_update_exercise_data_is_empty_failure(self):
        # Arrange
        exercise_id = 1
        exercise_example = {
            "name": None,
            "description": None
        }
        category = Category.BACK
        self.service.get_exercise = AsyncMock()
        self.mock_db.exercises.update = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act
        with pytest.raises(DataIsEmptyException):
            await self.service.partially_update_exercise(exercise_id, exercise_example, category)

        # Assert
        self.service.get_exercise.assert_not_called()
        self.mock_db.exercises.update.assert_not_called()
        self.mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_partially_update_exercise_obj_not_found_failure(self):
        # Arrange
        exercise_id = 1
        exercise_example = {
            "name": "Подтягивания",
            "description": "Базовое упражнение на спину"
        }
        self.service.get_exercise = AsyncMock(side_effect=ObjectNotFoundException)
        self.mock_db.exercises.update = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act = Assert
        with pytest.raises(ObjectNotFoundException):
            await self.service.partially_update_exercise(exercise_id, exercise_example, Category.BACK)

        # Assert
        self.service.get_exercise.assert_called_once_with(exercise_id)
        self.mock_db.exercises.update.assert_not_called()
        self.mock_db.commit.assert_not_called()