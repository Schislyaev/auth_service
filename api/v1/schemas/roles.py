import uuid

from pydantic import BaseModel, validator
from pydantic.types import constr

from core.logger import log
from db.postgres import db
from models.roles import Role as RoleModel

logger = log(__name__)


class Role(BaseModel):
    id: uuid.UUID
    name: constr(min_length=4, max_length=60)
    description: constr(min_length=0, max_length=200)

    class Config:
        orm_mode = True


class RoleList(BaseModel):
    results: list[Role]

    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    name: constr(min_length=1, max_length=15)
    description: constr(min_length=0, max_length=200)
    endpoint_ids: list[uuid.UUID] = []

    @validator('name')
    def is_name_unique(cls, name):
        if db.session.query(RoleModel).filter(RoleModel.name == name).count():
            logger.error('Role with which name already exists')
            raise ValueError('Role with which name already exists')
        return name


class RoleUpdate(BaseModel):
    name: str | None
    description: constr(min_length=0, max_length=200)
    endpoint_ids: list[uuid.UUID] | None

    @validator('name')
    def is_name_unique(cls, name):
        if name is not None and db.session.query(RoleModel).filter(RoleModel.name == name).count():
            logger.error('Role with which name already exists')
            raise ValueError('Role with which name already exists')
        return name
