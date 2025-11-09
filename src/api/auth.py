from fastapi import APIRouter, HTTPException, Depends
from jwt import ExpiredSignatureError
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.api.dependency import DBDep, UserDep
from src.exceptions import (
    EmailIsAlreadyRegisteredException,
    RegisterErrorException,
    LoginErrorException,
)
from src.schemas.users import UserRequest
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация и авторизация"])


@router.post(
    "/register",
    summary="Регистрация",
    description="Регистрация пользователя",
)
async def register_user(db: DBDep, data: UserRequest):
    try:
        user = await AuthService(db).register_user(data)
    except EmailIsAlreadyRegisteredException:
        raise HTTPException(status_code=409, detail="Email уже используется")
    except RegisterErrorException:
        raise HTTPException(status_code=400, detail="Ошибка регистрации")
    return user


@router.post(
    "/login",
    summary="Аутентификация",
    description="Аутентификация пользователя",
)
async def login_user(data: UserRequest, response: Response, db: DBDep):
    try:
        access_token = await AuthService(db).login_and_get_access_token(data=data)
    except LoginErrorException:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get(
    "/me",
    summary="👨‍💻 Мой профиль",
    description="Получить мой профиль",
)
async def get_me(user: UserDep, db: DBDep):
    user_id = user["user_id"]
    user = await AuthService(db).get_one_or_none_user(user_id)
    return user

@router.get(path="/register_confirm", status_code=status.HTTP_200_OK)
async def confirm_registration(token: str, db: DBDep) -> dict[str, str]:
    await AuthService(db).confirm_user(token=token)
    return {"message": "Электронная почта подтверждена"}

async def get_current_user(request: Request):
    try:
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Не авторизован")
        return AuthService().decode_token(access_token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен просрочен")


@router.post(
    "/logout",
    summary="Выйти из системы",
)
async def logout(response: Response, current_user=Depends(get_current_user)):
    response.delete_cookie("access_token")
    return {"status": "Вы вышли из системы"}
