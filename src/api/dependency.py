from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.requests import Request

from src.core.db import async_session_maker
from src.core.db_manager import DBManager
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

def get_current_user_id(token=Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data["user_id"]


UserIdDep: type[int] = Annotated[int, Depends(get_current_user_id)]