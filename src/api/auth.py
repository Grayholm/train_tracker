import logging

from fastapi import APIRouter, HTTPException, Depends
from itsdangerous import BadSignature
from jwt import ExpiredSignatureError
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.api.dependency import DBDep, UserDep, get_token, get_current_user
from src.exceptions import (
    EmailIsAlreadyRegisteredException,
    RegisterErrorException,
    LoginErrorException,
)
from src.schemas.users import UserRequest, UserAdd, ChangePasswordRequest
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

@router.get(path="/register_confirm", status_code=status.HTTP_200_OK, include_in_schema=False)
async def confirm_registration(db: DBDep, token: str) -> dict[str, str]:
    try:
        await AuthService(db).confirm_user(token=token)
        return {"message": "Электронная почта подтверждена"}
    except BadSignature:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный или просроченный токен"
            )

async def get_current_user_for_logout(request: Request):
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
async def logout(db: DBDep, response: Response, current_user=Depends(get_current_user_for_logout)):
    user_id = current_user["user_id"]
    response.delete_cookie("access_token")
    await AuthService(db).logout(user_id)
    return {"status": "Вы вышли из системы"}


@router.patch(
    "/edit_email",
    summary="Поменять почту"
)
async def change_email(db: DBDep, new_email: str, current_user=Depends(get_current_user)):
    try:
        old_email = current_user["user_email"]
        user_id = current_user["user_id"]
        await AuthService(db).change_email(new_email=new_email, old_email=old_email, user_id=user_id)
        return {
            "message": "На вашу новую почту отправлено письмо для подтверждения."
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/edit_password",
    summary="Поменять пароль"
)
async def change_password(db: DBDep, data: ChangePasswordRequest, current_user=Depends(get_current_user)):
    try:
        await AuthService(db).change_password(
            old_password=data.old_password,
            new_password=data.new_password,
            users_hashed_password=current_user["user_hashed_password"],
            user_id=current_user["user_id"]
        )
        return {"message": "Пароль успешно изменен"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Error changing password for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при изменении пароля"
        )