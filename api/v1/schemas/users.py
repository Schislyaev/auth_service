from pydantic import BaseModel
from pydantic.networks import EmailStr
from pydantic.types import constr


class UserPasswordModel(BaseModel):
    password: constr(min_length=4, max_length=60)


class UserModel(UserPasswordModel):
    email: EmailStr
    is_superuser: bool = False

    class Config:
        orm_mode = True


class UsersList(BaseModel):
    users: list[UserModel]

    class Config:
        orm_mode = True
