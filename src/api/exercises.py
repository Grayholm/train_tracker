from fastapi import APIRouter, HTTPException, Query
from fastapi_cache.decorator import cache

from src.api.dependency import DBDep, UserDep, check_is_admin
from src.exceptions import (
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
    DataIsEmptyException,
)
from src.schemas.exercises import (
    ExerciseUpdatePut,
    ExerciseUpdatePatch,
    Category,
    ExerciseAddRequest,
)
from src.services.exercises import ExercisesService

router = APIRouter(prefix="/exercises", tags=["Упражнения"])


@router.get("", summary="Доступные упражнения")
@cache(expire=3600)
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
async def add_exercise(
    db: DBDep,
    user: UserDep,
    exercise: ExerciseAddRequest,
    category: Category = Query(..., description="Категория упражнения"),
):
    check_is_admin(user)

    exercise_data_dict = exercise.model_dump()
    exercise_data_dict["category"] = category

    try:
        created = await ExercisesService(db).add_exercise(exercise_data_dict)
        return created
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=409, detail=f"Упражнение с name={exercise.name} уже существует"
        )


@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id: int, db: DBDep, user: UserDep):
    check_is_admin(user)

    try:
        await ExercisesService(db).delete_exercise(exercise_id)
        raise HTTPException(
            status_code=200, detail=f"Упражнение с ID={exercise_id} успешно удален"
        )
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail=f"Упражнение с ID={exercise_id} не найден")


@router.put("/{exercise_id}", summary="Изменить все данные упражнения")
async def update_exercise(
    db: DBDep,
    user: UserDep,
    exercise_id: int,
    exercise: ExerciseUpdatePut,
    category: Category = Query(..., description="Категория упражнения"),
):
    check_is_admin(user)

    exercise_data_dict = exercise.model_dump(exclude_unset=True)

    try:
        result = await ExercisesService(db).update_exercise(
            exercise_id, exercise_data_dict, category
        )
        return result
    except DataIsEmptyException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Объект не найден")


@router.patch("/{exercise_id}", summary="Изменить часть данных упражнения")
async def partially_update_exercise(
    db: DBDep,
    user: UserDep,
    exercise_id: int,
    exercise: ExerciseUpdatePatch,
    category: Category | None = Query(None, description="Категория упражнения"),
):
    check_is_admin(user)

    exercise_data_dict = exercise.model_dump(exclude_unset=True)

    try:
        result = await ExercisesService(db).partially_update_exercise(
            exercise_id, exercise_data_dict, category
        )
        return result
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Объект не найден")
    except DataIsEmptyException as e:
        raise HTTPException(status_code=400, detail=str(e))
