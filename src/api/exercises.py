from fastapi import APIRouter, HTTPException

from src.api.dependency import DBDep, UserDep, check_is_admin
from src.exceptions import ObjectNotFoundException
from src.schemas.exercises import ExerciseAdd
from src.services.exercises import ExercisesService

router = APIRouter(prefix="/exercises", tags=["Упражнения"])


@router.get("", summary="Доступные упражнения")
async def get_exercises(db: DBDep):
    exercises = await ExercisesService(db).get_exercises()
    return exercises


@router.get(
    "/{exercise_id}",
    summary="1 упражнение",
    description="Получить информацию о конкретном упражнении",
)
async def get_exercise(exercise_id: int, db: DBDep):
    try:
        exercise = await ExercisesService(db).get_exercise(exercise_id)
        return exercise
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Не найдено такого упражнения")


@router.post("", summary="Добавить упражнение")
async def add_exercise(exercise: ExerciseAdd, db: DBDep, user: UserDep):
    is_admin = check_is_admin(user)

    if not is_admin:
        raise HTTPException(status_code=403, detail="Вы не админ")

    created = await ExercisesService(db).add_exercise(exercise)
    return created
