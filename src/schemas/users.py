from enum import Enum

from pydantic import EmailStr, BaseModel


class Roles(Enum):
    USER = "user"
    ADMIN = "admin"


class UserRequest(BaseModel):
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str
    role: Roles = Roles.USER


class User(UserAdd):
    id: int
