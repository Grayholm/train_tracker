import pytest

@pytest.mark.parametrize(
        "date, description, exercise, status_code", [
            ("2025-02-02", "Утрення тренировка", {"id": 1, "sets": 3, "reps": 12, "weight": 50.0}, 200),
            ("2025-03-15", "Вечерняя тренировка", {"id": 2, "sets": 4, "reps": 10, "weight": 30.0}, 200),
            ("2025-04-10", None, {"id": 3, "sets": 5, "reps": 8, "weight": 20.0}, 200),
            ("2025-05-05", "Тренировка без упражнений", None, 422),
        ]
)
async def test_add_workout(authenticated_ac, date, description, exercise, status_code):
    response = await authenticated_ac.post(
        "/workouts",
        json = {
                "date": date,
                "description": description,
                "exercises": [exercise],
        }
    )

    assert response.status_code == status_code
    if response.status_code == 200:
        data = response.json()
        assert data["date"] == date
        assert data["description"] == description
