from dataclasses import dataclass

from flask import abort
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError

from api.v1.schemas import roles
from core.logger import log
from db.postgres import db
from models.endpoints import Endpoint
from models.roles import Role

logger = log(__name__)


@dataclass
class RolesService:
    model: Role = Role
    database: SQLAlchemy = db

    def get_list(self) -> list[roles.Role]:
        sa_roles = self.database.session.query(self.model).all()
        results = roles.RoleList(results=sa_roles)
        return results

    def create(self, role_data: dict):
        try:
            new_role_data = roles.RoleCreate(**role_data)
        except ValidationError as e:
            logger.exception(e)
            abort(400)

        role = self.model(**new_role_data.dict(exclude={'endpoint_ids'}))

        if new_role_data.endpoint_ids:
            endpoints = self.database.session.query(Endpoint).filter(Endpoint.id.in_(new_role_data.endpoint_ids)).all()
            for endpoint in endpoints:
                role.endpoints.append(endpoint)

        self.database.session.add(role)
        try:
            self.database.session.commit()
        except Exception as e:
            self.database.session.rollback()
            logger.exception(e)
            abort(500)

    def update(self, role_id: str, new_role_data: dict):
        try:
            validated_data = roles.RoleUpdate(**new_role_data)
        except ValidationError as e:
            logger.exception(e)
            abort(400)

        role = self.database.session.query(self.model). \
            filter(self.model.id == role_id). \
            first()
        if not role:
            logger.error('No such role')
            abort(404)

        new_data = validated_data.dict(exclude={'endpoint_ids'}, exclude_none=True)
        for key, value in new_data.items():
            setattr(role, key, value)

        if validated_data.endpoint_ids:
            endpoints = self.database.session.query(Endpoint). \
                filter(Endpoint.id.in_(validated_data.endpoint_ids)).all()
            role.endpoints[:] = endpoints

        try:
            self.database.session.commit()
        except Exception as e:
            self.database.session.rollback()
            logger.exception(e)
            abort(500)

    def delete(self, role_id: str):
        self.database.session.query(self.model).filter(self.model.id == role_id).delete()
        try:
            self.database.session.commit()
        except Exception as e:
            self.database.session.rollback()
            logger.exception(e)
            abort(500)
