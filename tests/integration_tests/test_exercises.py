import pytest

@pytest.mark.parametrize(
        "name, description, category, status_code", [
            ("Приседания", "Базовое упражнение приседания", "legs", 200),
            ("Бег на месте", "Кардио упражнение бег на месте", "cardio", 200),
            ("Приседания", "Повторное добавление упражнения приседания", "legs", 409),
            ("Жим лежа", None, "chest", 200),
            (None, "Описание без названия", "back", 422),
            ("", "Упражнение для бицепса", "arms", 422),
            ("   ", "Упражнение для бицепса", "arms", 422),
            ("Планка", "Упражнение для кора", "invalid_category", 422),
        ]
)
async def test_add_exercise(admin_ac, name, description, category, status_code):
    response = await admin_ac.post(
        f"/exercises?category={category}",
        json={
            "name": name,
            "description": description,
        },
    )

    assert response.status_code == status_code
    if status_code == 200:
        payload = response.json()
        assert payload["name"] == name
        assert payload["description"] == description

async def test_get_exercises(admin_ac):
    exercises_to_add = [
        {"name": "Отжимания", "description": "Упражнение для груди", "category": "chest"},
        {"name": "Подтягивания", "description": "Упражнение для спины", "category": "back"},
    ]
    for exercise in exercises_to_add:
        await admin_ac.post(
            f"/exercises?category={exercise['category']}",
            json={
                "name": exercise["name"],
                "description": exercise["description"],
            },
        )

    response = await admin_ac.get("/exercises")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= len(exercises_to_add)
    names = [ex["name"] for ex in payload]
    for exercise in exercises_to_add:
        assert exercise["name"] in names

@pytest.mark.parametrize(
    "name, description, exercise_id, status_code", [
        ("Приседания", "Базовое упражнение приседания", 1, 200),
        ("Бег на месте", "Кардио упражнение бег на месте", 2, 200),
        ("Неизвестное упражнение", "Описание несуществующего упражнения", 999, 404),
    ]
)
async def test_get_exercise(admin_ac, name, description, exercise_id, status_code):
    get_response = await admin_ac.get(f"/exercises/{exercise_id}")
    assert get_response.status_code == status_code
    if status_code == 200:
        fetched_exercise = get_response.json()
        assert fetched_exercise["name"] == name
        assert fetched_exercise["description"] == description

@pytest.mark.parametrize(
        "exercise_id, delete_status_code, get_status_code", [
            (4, 200, 404),
            (5, 200, 404),
            (999, 404, 404),
        ]
)
async def test_delete_exercise(admin_ac, exercise_id, delete_status_code, get_status_code):
    delete_response = await admin_ac.delete(f"/exercises/{exercise_id}")
    assert delete_response.status_code == delete_status_code

    if delete_status_code == 200:
        get_response = await admin_ac.get(f"/exercises/{exercise_id}")
        assert get_response.status_code == get_status_code

@pytest.mark.parametrize(
        "name, description, exercise_id, status_code", [
            ("Выпады назад", "Обновленное упражнение для ног", 1, 200),
            ("Прыжки", "Обновленное кардио упражнение", 2, 200),
            (None, "Описание несуществующего упражнения", 3, 422),
            ("Прыжки", None, 3, 422),
            ("", "Описание несуществующего упражнения", 3, 422),
            ("Прыжки", "", 3, 422),
            ("Неизвестное упражнение", "Описание несуществующего упражнения", 999, 404),
        ]
)
async def test_update_exercise(admin_ac, name, description, exercise_id, status_code):
    update_response = await admin_ac.put(
        f"/exercises/{exercise_id}?category=legs",
        json={
            "name": name,
            "description": description,
        },
    )
    assert update_response.status_code == status_code
    if update_response.status_code == 200:
        updated_exercise = update_response.json()
        assert updated_exercise["name"] == name
        assert updated_exercise["description"] == description

@pytest.mark.parametrize(
        "name, description, exercise_id, status_code", [
            ("Выпады вперед", "Частично обновленное упражнение для ног", 1, 200),
            ("Прыжки в длину", "Частично обновленное кардио упражнение", 2, 200),
            (None, "Описание несуществующего упражнения", 3, 422),
            ("Прыжки", None, 3, 200),
            ("", "Описание несуществующего упражнения", 3, 422),
            ("Прыжки", "", 3, 200),
            ("Неизвестное упражнение", "Описание несуществующего упражнения", 999, 404),
        ]
)
async def test_partially_update_exercise(admin_ac, name, description, exercise_id, status_code):
    partial_update_response = await admin_ac.patch(
        f"/exercises/{exercise_id}?category=legs",
        json={
            "name": name,
            "description": description,
        },
    )
    assert partial_update_response.status_code == status_code
    if partial_update_response.status_code == 200:
        partially_updated_exercise = partial_update_response.json()
        assert partially_updated_exercise["name"] == name
        assert partially_updated_exercise["description"] == description