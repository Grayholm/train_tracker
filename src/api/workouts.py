from fastapi import APIRouter, HTTPException

from src.api.dependency import UserDep, DBDep
from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
from src.schemas.workouts import WorkoutRequest, WorkoutUpdate
from src.services.workouts import WorkoutsService

router = APIRouter(prefix="/workouts", tags=["Мои тренировки"])


@router.get("", summary="Мои тренировки")
async def get_all_my_workouts(db: DBDep, user: UserDep):
    user_id = user["user_id"]
    workouts = await WorkoutsService(db).get_workouts(user_id)
    return workouts


@router.get("/{workout_id}", summary="Тренировка {workout_id}")
async def get_workout(workout_id: int, db: DBDep, user: UserDep):
    try:
        exercise = await WorkoutsService(db).get_workout(workout_id)
        return exercise
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

@router.delete("/{workout_id}")
async def delete_workout(workout_id: int, db: DBDep, user: UserDep):
    user_id = user["user_id"]
    try:
        await WorkoutsService(db).delete_workout(user_id, workout_id)
        return HTTPException(
            status_code=200, detail=f"Тренировка с ID={workout_id} успешно удалена"
        )
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail=f"Тренировка с ID={workout_id} не найдена либо не принадлежит вам")


@router.put("/{workout_id}")
async def update_workout(workout_id: int, workout: WorkoutUpdate, user: UserDep):
    pass


@router.patch("/{workout_id}")
async def partially_update_workout(workout_id: int, workout: WorkoutUpdate, user: UserDep):
    pass
