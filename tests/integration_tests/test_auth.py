import pytest


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("johndoe@gmail.com", "zalusdpa", 200),
        ("john1doe@gmail.com", "zaluasdpa", 200),
        ("john1doe@gmail.com", "zaluasdpa", 409),
        ("alexdoe@gmail.com", "adsd", 422),
        ("alexdoe1@gmail.com", "", 422),
        ("alexdoe1", "dfhgsdfg", 422),
    ]
)
async def test_register_user(
    email,
    password,
    status_code,
    ac,
    patch_celery_delay,
):
    response = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == status_code
    if status_code == 200:
        patch_celery_delay.assert_called_once()

@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("johndoe@gmail.com", "zalusdpa", 200),
        ("johndoe2@gmail.com", "zalusdpa", 401),
        ("johndoe@gmail.com", "dfsglksga", 401),
        ("johndoe@gmail", "zalusdpa", 422),
        ("", "zalusdpa", 422),
    ],
)
async def test_login_user(
    email,
    password,
    status_code,
    ac,
):
    response = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == status_code

    if status_code == 200:
        payload = response.json()
        assert "access_token" in payload
        token = payload["access_token"]
        assert token != ""  # не пустой

        assert ac.cookies["access_token"] == token


async def test_get_me(authenticated_ac):
    response = await authenticated_ac.get(
        "/auth/me",
    )
    assert response.status_code == 200
    assert "email" in response.json()
    assert "id" in response.json()
    print(response.json())


async def test_logout(authenticated_ac):
    response = await authenticated_ac.post(
        "/auth/logout",
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Вы вышли из системы"
    assert "access_token" not in authenticated_ac.cookies