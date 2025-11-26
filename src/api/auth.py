import logging

from fastapi import APIRouter, HTTPException, Depends
from itsdangerous import BadSignature
from jwt import ExpiredSignatureError
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse

from src.api.dependency import DBDep, UserDep, get_current_user
from src.exceptions import (
    EmailIsAlreadyRegisteredException,
    RegisterErrorException,
    LoginErrorException,
)
from src.schemas.users import UserRequest, ChangePasswordRequest
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


#####ДЛЯ ТАСКА СЕЛЬДЕРЕЙ#####
@router.get(
    path="/register_confirm",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def confirm_registration(db: DBDep, token: str) -> HTMLResponse:
    try:
        await AuthService(db).confirm_user(token=token)

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email подтвержден!</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Email успешно подтвержден!</h1>
                <p>Добро пожаловать! Наслаждайтесь:</p>

                <video width="640" height="360" controls autoplay loop muted>
                    <source src="/static/NGGYU/secret.mp4" type="video/mp4">
                    Ваш браузер не поддерживает видео.
                </video>

            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except BadSignature:
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ошибка подтверждения</title>
            <style>body { font-family: Arial; text-align: center; padding: 50px; }</style>
        </head>
        <body>
            <h1 style="color: red;">❌ Ошибка подтверждения</h1>
            <p>Неверный или просроченный токен</p>
            <p><a href="/">Вернуться на главную</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)


#####ДЛЯ ТАСКА СЕЛЬДЕРЕЙ#####


async def get_current_user_for_logout(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Не авторизован")

    try:
        return AuthService().decode_token(access_token)
    except ExpiredSignatureError:
        # Разрешаем выход даже с просроченным токеном
        return {"user_id": None, "expired": True}
    except Exception:
        # Разрешаем выход даже с невалидным токеном
        return {"user_id": None, "invalid": True}


@router.post(
    "/logout",
    summary="Выйти из системы",
)
async def logout(db: DBDep, response: Response, current_user=Depends(get_current_user_for_logout)):
    user_id = current_user.get("user_id")
    response.delete_cookie("access_token")

    if user_id:
        await AuthService(db).logout(user_id)
        return {"status": "Вы вышли из системы"}
    else:
        return {"status": "Сессия завершена"}


@router.patch("/edit_email", summary="Поменять почту")
async def change_email(db: DBDep, new_email: str, current_user=Depends(get_current_user)):
    try:
        old_email = current_user["user_email"]
        user_id = current_user["user_id"]
        await AuthService(db).change_email(
            new_email=new_email, old_email=old_email, user_id=user_id
        )
        return {"message": "На вашу новую почту отправлено письмо для подтверждения."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/edit_password", summary="Поменять пароль")
async def change_password(
    db: DBDep, data: ChangePasswordRequest, current_user=Depends(get_current_user)
):
    try:
        await AuthService(db).change_password(
            old_password=data.old_password,
            new_password=data.new_password,
            users_hashed_password=current_user["user_hashed_password"],
            user_id=current_user["user_id"],
        )
        return {"message": "Пароль успешно изменен"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.error(f"Error changing password for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при изменении пароля",
        )

def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b