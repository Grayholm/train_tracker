from fastapi import APIRouter, HTTPException

from src.api.dependency import UserDep, DBDep
from src.exceptions import ObjectNotFoundException, DataIsEmptyException, AccessDeniedException
from src.schemas.workouts import WorkoutRequest, WorkoutUpdatePatch, ExerciseToAdd
from src.services.workouts import WorkoutsService

router = APIRouter(prefix="/workouts", tags=["Мои тренировки"])


@router.get("", summary="Мои тренировки")
async def get_all_my_workouts(db: DBDep, user: UserDep):
    user_id = user["user_id"]
    workouts = await WorkoutsService(db).get_workouts(user_id)
    return workouts


@router.get("/get/{workout_id}", summary="Тренировка {workout_id}")
async def get_workout(workout_id: int, db: DBDep, user: UserDep):
    try:
        workout = await WorkoutsService(db).get_workout(workout_id)
        return workout
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Не найдено такой тренировки")


@router.post("")
async def add_workout(workout: WorkoutRequest, db: DBDep, user: UserDep):
    user_id = user["user_id"]
    try:
        created = await WorkoutsService(db).add_workout(user_id, workout)
        return created
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/delete/{workout_id}")
async def delete_workout(workout_id: int, db: DBDep, user: UserDep):
    user_id = user["user_id"]
    try:
        await WorkoutsService(db).delete_workout(user_id, workout_id)
        return HTTPException(
            status_code=200, detail=f"Тренировка с ID={workout_id} успешно удалена"
        )
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=404,
            detail=f"Тренировка с ID={workout_id} не найдена либо не принадлежит вам",
        )


@router.patch("/edit/{workout_id}")
async def partially_update_workout(
    workout_id: int, workout: WorkoutUpdatePatch, db: DBDep, user: UserDep
):
    user_id = user["user_id"]
    try:
        result = await WorkoutsService(db).partially_update_workout(user_id, workout_id, workout)
        return HTTPException(status_code=200, detail=result)
    except DataIsEmptyException:
        raise HTTPException(status_code=403, detail="Данные не могут быть пусты")
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Объект не найден")


@router.patch("/{workout_id}")
async def add_exercises_to_workout(
    workout_id: int, exercise_to_workout: list[ExerciseToAdd], db: DBDep, user: UserDep
):
    user_id = user["user_id"]
    try:
        created = await WorkoutsService(db).add_exercises_to_workout(
            user_id, workout_id, exercise_to_workout
        )
        return created
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
