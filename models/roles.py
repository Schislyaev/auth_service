import uuid

from flask_security import RoleMixin
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import db
from models.endpoints import Endpoint

roles_endpoints = db.Table(
    'roles_endpoints',
    db.Column('endpoint_id', UUID(as_uuid=True), db.ForeignKey('endpoint.id', ondelete='CASCADE')),
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('role.id', ondelete='CASCADE'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    endpoints = db.relationship(Endpoint, secondary=roles_endpoints)
