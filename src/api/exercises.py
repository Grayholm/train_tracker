from fastapi import APIRouter, HTTPException

from src.api.dependency import DBDep, UserDep, check_is_admin
from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
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
    check_is_admin(user)

    try:
        created = await ExercisesService(db).add_exercise(exercise)
        return created
    except ObjectAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=f"Упражнение с name={exercise.name} уже существует")

@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id: int, db: DBDep, user: UserDep):
    check_is_admin(user)

    try:
        await ExercisesService(db).delete_exercise(exercise_id)
        return HTTPException(status_code=200, detail=f"Упражнение с ID={exercise_id} успешно удален")
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=f"Упражнение с ID={exercise_id} не найден")

@router.put("/{exercise_id}", summary="Изменить все данные упражнения")
async def update_exercise(exercise_id: int, db: DBDep, user: UserDep):
    pass

@router.patch("/{exercise_id}", summary="Изменить часть данных упражнения")
async def partially_update_exercise(exercise_id: int, db: DBDep, user: UserDep):
    pass