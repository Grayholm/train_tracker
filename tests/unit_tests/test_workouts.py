import datetime
from unittest.mock import AsyncMock, Mock
from sqlalchemy.exc import NoResultFound

import pytest

from src.exceptions import ObjectNotFoundException
from src.schemas.exercises import Exercise, Category
from src.schemas.workouts import WorkoutAdd, WorkoutExercise, Workout, ExerciseToAdd, WorkoutExerciseAdd, WorkoutRequest
from src.services.workouts import WorkoutsService
from tests.base_test import BaseTestService


class TestWorkoutsService(BaseTestService):
    service_name = WorkoutsService

    def setup_method(self):
        super().setup_method()
        self.service = WorkoutsService(db=self.mock_db)

    @pytest.mark.asyncio
    async def test_get_workouts(self):
        # Arrange
        user_id = 12
        self.mock_db.workouts.get_filtered = AsyncMock(return_value=[])

        # Act
        workouts = await self.service.get_workouts(user_id=user_id)

        # Assert
        assert workouts == []
        self.mock_db.workouts.get_filtered.assert_called_once_with(user_id=user_id)

    @pytest.mark.asyncio
    async def test_get_workout_success(self):
        # Arrange
        workout_id = 12
        workout_example = Workout(
            id=12,
            user_id=32,
            date=datetime.date(2025, 2, 2),
            description="Базовое упражнение",
        )
        workouts_exercise_example = WorkoutExercise(
            workout_id=12,
            exercise_id=9,
            sets=5,
            reps=12,
            weight=80,
        )
        self.mock_db.workouts.get_one = AsyncMock(return_value=workout_example)
        self.mock_db.workout_exercises.get_filtered = AsyncMock(return_value=[workouts_exercise_example])

        # Act
        workout = await self.service.get_workout(workout_id)

        # Assert
        self.mock_db.workouts.get_one.assert_called_once_with(id=workout_id)
        self.mock_db.workout_exercises.get_filtered.assert_called_once_with(workout_id=workout_id)
        assert workout.id == workout_id
        assert workout.user_id == 32
        assert workout.date == datetime.date(2025, 2, 2)
        assert workout.description == "Базовое упражнение"
        assert workout.exercises == [workouts_exercise_example]

    @pytest.mark.asyncio
    async def test_get_workout_obj_not_found_failure(self):
        # Arrange
        self.mock_db.workouts.get_one = AsyncMock(side_effect=NoResultFound)
        self.mock_db.workout_exercises.get_filtered = AsyncMock()

        # Act
        with pytest.raises(ObjectNotFoundException):
            await self.service.get_workout(123)

        # Assert
        self.mock_db.workouts.get_one.assert_called_once_with(id=123)
        self.mock_db.workout_exercises.get_filtered.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_workout_success(self):
        # Arrange
        user_id = 5555
        exercise_for_workouts_example = ExerciseToAdd(
            id=1,
            sets=4,
            reps=15,
            weight=80,
        )
        exercise_example = Exercise(
            id=1,
            name="Жим лежа",
            description="Базовое упражнение на грудь",
            category=Category.CHEST,
        )
        workout_request_example = WorkoutRequest(
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
            exercises=[exercise_for_workouts_example]
        )
        workout_example = Workout(
            id=123,
            user_id=5555,
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
        )
        self.mock_db.exercises.get_one = AsyncMock(return_value=exercise_example)
        self.mock_db.workouts.add = AsyncMock(return_value=workout_example)
        self.mock_db.workout_exercises.add = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act
        workout = await self.service.add_workout(user_id, workout_request_example)

        # Assert
        assert workout.id == workout_example.id
        assert workout.user_id == 5555
        expected_workout = WorkoutAdd(
            user_id=5555,
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
        )
        self.mock_db.exercises.get_one.assert_called_once_with(id=1)
        self.mock_db.workouts.add.assert_called_once_with(expected_workout)
        called_workout = self.mock_db.workouts.add.call_args[0][0]
        assert called_workout.user_id == expected_workout.user_id
        assert called_workout.date == expected_workout.date
        assert called_workout.description == expected_workout.description

        self.mock_db.workout_exercises.add.assert_called_once()
        called_workout_ex = self.mock_db.workout_exercises.add.call_args[0][0]
        assert called_workout_ex.workout_id == workout_example.id
        assert called_workout_ex.exercise_id == exercise_for_workouts_example.id
        assert called_workout_ex.sets == exercise_for_workouts_example.sets
        assert called_workout_ex.reps == exercise_for_workouts_example.reps
        assert called_workout_ex.weight == exercise_for_workouts_example.weight

        self.mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_workout_obj_not_found_failure(self):
        pass

    @pytest.mark.asyncio
    async def test_add_exercises_to_workout(self):
        pass

    @pytest.mark.asyncio
    async def test_add_exercises_to_workout_obj_not_found_failure(self):
        pass

    @pytest.mark.asyncio
    async def test_add_exercises_to_workout_access_denied_failure(self):
        pass

    @pytest.mark.asyncio
    async def test_delete_workout(self):
        pass

    @pytest.mark.asyncio
    async def test_delete_workout_obj_not_found_failure(self):
        pass

    @pytest.mark.asyncio
    async def test_partially_update_workout(self):
        pass

    @pytest.mark.asyncio
    async def test_partially_update_workout_obj_not_found_failure(self):
        pass

    @pytest.mark.asyncio
    async def test_partially_update_workout_data_is_empty_failure(self):
        pass