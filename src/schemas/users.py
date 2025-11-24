from enum import Enum

from pydantic import EmailStr, BaseModel, Field


class Roles(Enum):
    USER = "user"
    ADMIN = "admin"


class UserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str
    role: Roles = Roles.USER


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=6, max_length=64)
    new_password: str = Field(min_length=6, max_length=64)


class User(UserAdd):
    id: int
