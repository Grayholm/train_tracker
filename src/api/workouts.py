from fastapi import APIRouter

from src.api.dependency import UserDep
from src.schemas.workouts import WorkoutRequest, WorkoutUpdate

router = APIRouter(prefix="/workouts", tags=["Мои тренировки"])


@router.get("")
async def get_all_my_workouts(user: UserDep):
    pass


@router.get("/{workout_id}")
async def get_workout(workout_id: int, user: UserDep):
    pass


@router.post("")
async def add_workout(workout: WorkoutRequest, user: UserDep):
    pass


@router.delete("/{workout_id}")
async def delete_workout(workout_id: int, user: UserDep):
    pass


@router.put("/{workout_id}")
async def update_workout(workout_id: int, workout: WorkoutUpdate, user: UserDep):
    pass


@router.patch("/{workout_id}")
async def partially_update_workout(workout_id: int, workout: WorkoutUpdate, user: UserDep):
    pass
