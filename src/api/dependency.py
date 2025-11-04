from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.requests import Request

from src.core.db import async_session_maker
from src.core.db_manager import DBManager
from src.schemas.users import Roles
from src.services.auth import AuthService


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep: type[DBManager] = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не предоставили куки-токен")

    return access_token


def get_current_user(token=Depends(get_token)) -> dict:
    data = AuthService().decode_token(token)
    data = {
        "user_id": data["user_id"],
        "user_role": data["user_role"],
    }
    return data


UserDep: type[dict] = Annotated[dict, Depends(get_current_user)]


def check_is_admin(user: UserDep):
    role_value = user["user_role"]
    if role_value == Roles.ADMIN.value:
        return True
    else:
        raise HTTPException(status_code=403, detail="Вы не админ")