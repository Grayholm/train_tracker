from sqlalchemy.exc import NoResultFound

from src.exceptions import DataIsEmptyException, ObjectNotFoundException, AccessDeniedException
from src.schemas.workouts import (
    WorkoutUpdate,
    WorkoutUpdatePatch,
    WorkoutAdd,
    WorkoutRequest,
    WorkoutExerciseAdd,
    WorkoutToResponse,
)
from src.services.base import BaseService


class WorkoutsService(BaseService):
    async def get_workouts(self, user_id: int):
        workouts = await self.db.workouts.get_filtered(user_id=user_id)
        return workouts

    async def get_workout(self, workout_id):
        try:
            workout_data = await self.db.workouts.get_one(id=workout_id)
            exercises_data = await self.db.workout_exercises.get_filtered(workout_id=workout_id)
            workout = WorkoutToResponse(
                id=workout_id,
                user_id=workout_data.user_id,
                date=workout_data.date,
                description=workout_data.description,
                exercises=exercises_data,
            )
            return workout
        except NoResultFound:
            raise ObjectNotFoundException

    async def add_workout(self, user_id: int, workout_example: WorkoutRequest):
        for exercise_data in workout_example.exercises:
            exercise_id = exercise_data.id
            try:
                await self.db.exercises.get_one(id=exercise_id)
            except ObjectNotFoundException:
                raise ObjectNotFoundException(f"Exercise with id {exercise_id} not found")
        workout = WorkoutAdd(
            user_id=user_id,
            date=workout_example.date,
            description=workout_example.description,
        )
        created_workout = await self.db.workouts.add(workout)

        for exercise_data in workout_example.exercises:
            workout_exercise_data = WorkoutExerciseAdd(
                workout_id=created_workout.id,
                exercise_id=exercise_data.id,
                sets=exercise_data.sets,
                reps=exercise_data.reps,
                weight=exercise_data.weight,
            )
            await self.db.workout_exercises.add(workout_exercise_data)

        await self.db.commit()
        return created_workout

    async def add_exercises_to_workout(self, user_id, workout_id, exercise_to_workout):
        try:
            await self.db.workout_exercises.get_one(id=workout_id)
        except ObjectNotFoundException:
            raise ObjectNotFoundException(f"Тренировка с таким ID {workout_id} не найдена")
        workout = await self.db.workouts.get_one(id=workout_id)
        if user_id != workout.user_id:
            raise AccessDeniedException(f"Данная тренировка с ID {workout_id} не принадлежит вам")

        for exercise_data in exercise_to_workout:
            workout_exercise_data = WorkoutExerciseAdd(
                workout_id=workout_id,
                exercise_id=exercise_data.id,
                sets=exercise_data.sets,
                reps=exercise_data.reps,
                weight=exercise_data.weight,
            )
            await self.db.workout_exercises.add(workout_exercise_data)

        await self.db.commit()

    async def delete_workout(self, user_id: int, workout_id: int):
        result = await self.db.workouts.get_one_or_none(id=workout_id, user_id=user_id)
        if result is None:
            raise ObjectNotFoundException
        try:
            await self.db.workouts.delete(id=workout_id)
            await self.db.commit()
        except ObjectNotFoundException:
            raise

    async def partially_update_workout(
        self, user_id: int, workout_id: int, workout: WorkoutUpdatePatch
    ):
        data_dict = workout.model_dump(exclude_unset=True) if workout else {}
        if not data_dict:
            return DataIsEmptyException("Отсутствуют данные для обновления")
        try:
            existed = await self.get_workout(workout_id)
        except ObjectNotFoundException:
            raise

        data = WorkoutUpdate(
            user_id=user_id,
            date=workout.date,
            description=workout.description,
        )

        result = await self.db.workouts.update(data, id=workout_id)
        for exercise_data in workout.exercises:
            workout_exercise_data = WorkoutExerciseAdd(
                workout_id=existed.id,
                exercise_id=exercise_data.id,
                sets=exercise_data.sets,
                reps=exercise_data.reps,
                weight=exercise_data.weight,
            )
            await self.db.workout_exercises.add(workout_exercise_data)
        await self.db.commit()
        return result
