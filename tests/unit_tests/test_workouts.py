import datetime
from unittest.mock import AsyncMock
from sqlalchemy.exc import NoResultFound

import pytest

from src.exceptions import AccessDeniedException, DataIsEmptyException, ObjectNotFoundException
from src.schemas.exercises import Exercise, Category
from src.schemas.workouts import WorkoutAdd, WorkoutExercise, Workout, ExerciseToAdd, WorkoutRequest, WorkoutUpdatePatch
from src.services.workouts import WorkoutsService
from tests.unit_tests.base_test import BaseTestService


class TestWorkoutsService(BaseTestService):
    service_name = WorkoutsService

    def setup_method(self):
        super().setup_method()
        self.service = WorkoutsService(db=self.mock_db)

    async def test_get_workouts(self):
        # Arrange
        user_id = 12
        self.mock_db.workouts.get_filtered = AsyncMock(return_value=[])

        # Act
        workouts = await self.service.get_workouts(user_id=user_id)

        # Assert
        assert workouts == []
        self.mock_db.workouts.get_filtered.assert_called_once_with(user_id=user_id)

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

    async def test_add_workout_obj_not_found_failure(self):
        # Arrange
        exercise_for_workouts_example = ExerciseToAdd(
            id=1,
            sets=4,
            reps=15,
            weight=80,
        )
        workout_request_example = WorkoutRequest(
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
            exercises=[exercise_for_workouts_example]
        )
        self.mock_db.exercises.get_one = AsyncMock(side_effect=NoResultFound)

        # Act & Assert
        with pytest.raises(ObjectNotFoundException):
            await self.service.add_workout(user_id=5555, workout_example=workout_request_example)

        # Assert
        self.mock_db.exercises.get_one.assert_called_once_with(id=1)

    async def test_add_exercises_to_workout_success(self):
        # Arrange
        user_id = 5555
        exercise_for_workouts_example = ExerciseToAdd(
            id=1,
            sets=4,
            reps=15,
            weight=80,
        )
        workout_example = Workout(
            id=123,
            user_id=5555,
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
        )
        self.mock_db.workouts.get_one_or_none = AsyncMock(return_value=workout_example)
        self.mock_db.workout_exercises.add = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act
        await self.service.add_exercises_to_workout(
            user_id=user_id,
            workout_id=123,
            exercise_to_workout=[exercise_for_workouts_example]
        )

        # Assert
        self.mock_db.workouts.get_one_or_none.assert_called_once_with(id=123)
        self.mock_db.workout_exercises.add.assert_called_once()
        self.mock_db.commit.assert_called_once()

    async def test_add_exercises_to_workout_obj_not_found_failure(self):
        # Arrange
        user_id = 5555
        exercise_for_workouts_example = ExerciseToAdd(
            id=1,
            sets=4,
            reps=15,
            weight=80,
        )
        workout_id = 123
        self.mock_db.workouts.get_one_or_none = AsyncMock(return_value=None)
        self.mock_db.workout_exercises.add = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act & Assert
        with pytest.raises(ObjectNotFoundException):
            await self.service.add_exercises_to_workout(
                user_id=user_id,
                workout_id=workout_id,
                exercise_to_workout=[exercise_for_workouts_example]
            )

        # Assert
        self.mock_db.workouts.get_one_or_none.assert_called_once_with(id=workout_id)
        self.mock_db.workout_exercises.add.assert_not_called()
        self.mock_db.commit.assert_not_called()

    async def test_add_exercises_to_workout_access_denied_failure(self):
        # Arrange
        user_id = 12
        exercise_for_workouts_example = ExerciseToAdd(
            id=1,
            sets=4,
            reps=15,
            weight=80,
        )
        workout_example = Workout(
            id=123,
            user_id=5555,
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
        )
        self.mock_db.workouts.get_one_or_none = AsyncMock(return_value=workout_example)
        self.mock_db.workout_exercises.add = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act & Assert
        with pytest.raises(AccessDeniedException):
            await self.service.add_exercises_to_workout(
                user_id=user_id,
                workout_id=123,
                exercise_to_workout=[exercise_for_workouts_example]
            )

        # Assert
        self.mock_db.workouts.get_one_or_none.assert_called_once_with(id=123)
        self.mock_db.workout_exercises.add.assert_not_called()
        self.mock_db.commit.assert_not_called()

    async def test_delete_workout(self):
        # Arrange
        user_id = 5555
        workout_id = 123
        workout_example = Workout(
            id=123,
            user_id=5555,
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
        )
        self.mock_db.workouts.get_one_or_none = AsyncMock(return_value=workout_example)
        self.mock_db.workouts.delete = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act
        await self.service.delete_workout(user_id=user_id, workout_id=workout_id)

        # Assert
        self.mock_db.workouts.get_one_or_none.assert_called_once_with(id=workout_id, user_id=user_id)
        self.mock_db.workouts.delete.assert_called_once_with(id=workout_id)
        self.mock_db.commit.assert_called_once()

    async def test_delete_workout_obj_not_found_failure(self):
        # Arrange
        user_id = 5555
        workout_id = 123
        self.mock_db.workouts.get_one_or_none = AsyncMock(return_value=None)
        self.mock_db.workouts.delete = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act & Assert
        with pytest.raises(ObjectNotFoundException):
            await self.service.delete_workout(user_id=user_id, workout_id=workout_id)

        # Assert
        self.mock_db.workouts.get_one_or_none.assert_called_once_with(id=workout_id, user_id=user_id)
        self.mock_db.workouts.delete.assert_not_called()
        self.mock_db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "date,description,exercises,expected_exercises_count",
        [
            # Все поля заполнены
            (
                datetime.date(2025, 3, 3),
                "Противоположное описание",
                [ExerciseToAdd(id=1, sets=4, reps=15, weight=80)],
                1,
            ),
            # Только описание
            (
                datetime.date(2025, 2, 2),  # дата обязательна, берем старую
                "Новое описание",
                None,
                0,
            ),
            # Только упражнения
            (
                datetime.date(2025, 2, 2),  # дата обязательна
                None,
                [ExerciseToAdd(id=2, sets=5, reps=10, weight=100)],
                1,
            ),
            # Дата и описание
            (
                datetime.date(2025, 4, 4),
                "Смешанное обновление",
                None,
                0,
            ),
            # Дата и упражнения
            (
                datetime.date(2025, 5, 5),
                None,
                [ExerciseToAdd(id=3, sets=3, reps=8, weight=50)],
                1,
            ),
            # Описание и упражнения
            (
                datetime.date(2025, 2, 2),  # дата обязательна
                "Только упражнения и описание",
                [ExerciseToAdd(id=4, sets=6, reps=20, weight=120)],
                1,
            ),
            # Несколько упражнений
            (
                datetime.date(2025, 6, 6),
                "Много упражнений",
                [
                    ExerciseToAdd(id=1, sets=4, reps=15, weight=80),
                    ExerciseToAdd(id=2, sets=5, reps=10, weight=100),
                ],
                2,
            ),
        ],
    )
    async def test_partially_update_workout_success(
        self,
        date,
        description,
        exercises,
        expected_exercises_count,
    ):
        # Arrange
        workout_id = 123
        user_id = 5555
        
        workout_example = WorkoutUpdatePatch(
            date=date,
            description=description,
            exercises=exercises,
        )
        
        existed_workout = Workout(
            id=123,
            user_id=5555,
            date=datetime.date(2025, 2, 2),
            description="Первая тренировка на грудь",
        )
        
        updated_workout = Workout(
            id=123,
            user_id=5555,
            date=date,
            description=description or existed_workout.description,
        )
        
        self.service.get_workout = AsyncMock(return_value=existed_workout)
        self.mock_db.workouts.update = AsyncMock(return_value=updated_workout)
        self.mock_db.workout_exercises.add = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act
        result = await self.service.partially_update_workout(
            user_id=user_id,
            workout_id=workout_id,
            workout=workout_example
        )

        # Assert
        self.service.get_workout.assert_called_once_with(workout_id)
        
        args, kwargs = self.mock_db.workouts.update.call_args
        data_arg = args[0]
        assert kwargs["id"] == workout_id
        assert data_arg.user_id == user_id
        assert data_arg.date == date
        assert data_arg.description == description
        
        assert self.mock_db.workout_exercises.add.call_count == expected_exercises_count
        if expected_exercises_count > 0:
            for i, exercise_data in enumerate(exercises):
                called_arg = self.mock_db.workout_exercises.add.call_args_list[i][0][0]
                assert called_arg.workout_id == existed_workout.id
                assert called_arg.exercise_id == exercise_data.id
                assert called_arg.sets == exercise_data.sets
                assert called_arg.reps == exercise_data.reps
                assert called_arg.weight == exercise_data.weight
        
        assert result.id == existed_workout.id
        assert result.user_id == existed_workout.user_id
        assert result.date == date
        self.mock_db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "date,description,exercises",
        [
            # Попытка обновить несуществующий воркаут - все поля заполнены
            (
                datetime.date(2025, 3, 3),
                "Противоположное описание",
                [ExerciseToAdd(id=1, sets=4, reps=15, weight=80)],
            ),
            # Попытка обновить несуществующий воркаут - только описание
            (
                datetime.date(2025, 2, 2),
                "Новое описание",
                None,
            ),
            # Попытка обновить несуществующий воркаут - только упражнения
            (
                datetime.date(2025, 2, 2),
                None,
                [ExerciseToAdd(id=1, sets=4, reps=15, weight=80)],
            ),
        ],
    )
    async def test_partially_update_workout_obj_not_found_failure(
        self, date, description, exercises
    ):
        # Arrange
        workout_id = 123
        user_id = 5555
        workout_example = WorkoutUpdatePatch(
            date=date,
            description=description,
            exercises=exercises,
        )
        self.service.get_workout = AsyncMock(side_effect=ObjectNotFoundException)
        self.mock_db.workouts.update = AsyncMock()
        self.mock_db.workout_exercises.add = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act & Assert
        with pytest.raises(ObjectNotFoundException):
            await self.service.partially_update_workout(
                user_id=user_id,
                workout_id=workout_id,
                workout=workout_example
            )

        # Assert
        self.service.get_workout.assert_called_once_with(workout_id)
        self.mock_db.workouts.update.assert_not_called()
        self.mock_db.workout_exercises.add.assert_not_called()
        self.mock_db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "description,exercises",
        [
            (None, None),
            (None, []),
        ],
    )
    async def test_partially_update_workout_data_is_empty_failure(
        self, description, exercises
    ):
        # Arrange
        workout_id = 123
        user_id = 5555
        workout_example = WorkoutUpdatePatch(
            description=description,
            exercises=exercises,
        )
        self.service.get_workout = AsyncMock()
        self.mock_db.workouts.update = AsyncMock()
        self.mock_db.workout_exercises.add = AsyncMock()
        self.mock_db.commit = AsyncMock()

        # Act & Assert
        with pytest.raises(DataIsEmptyException):
            await self.service.partially_update_workout(
                user_id=user_id,
                workout_id=workout_id,
                workout=workout_example
            )

        # Assert
        self.service.get_workout.assert_not_called()
        self.mock_db.workouts.update.assert_not_called()
        self.mock_db.workout_exercises.add.assert_not_called()
        self.mock_db.commit.assert_not_called()