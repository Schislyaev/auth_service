import uuid
from datetime import datetime

from flask import Response, abort
from flask_api import status
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                decode_token)
from flask_security import UserMixin
from passlib.hash import bcrypt
from sqlalchemy import (ForeignKeyConstraint, PrimaryKeyConstraint,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID

from core.logger import log
from core.tracer.decorators import class_tracer
from db.postgres import db
from models.helpers import create_user_partition
from models.roles import Role
from models.tokens import RToken

logger = log(__name__)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', UUID(as_uuid=True)),
    db.Column('user_created_at', db.DateTime),
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('role.id', ondelete='CASCADE')),
    ForeignKeyConstraint(
        ('user_id', 'user_created_at'), ('user.id', 'user.created_at'), ondelete='CASCADE',
    ),
)


class User(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    is_superuser = db.Column(db.Boolean, nullable=False)

    roles = db.relationship(Role, secondary=roles_users)

    __tablename__ = 'user'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'created_at'),
        UniqueConstraint('email', 'created_at'),
        {
            'postgresql_partition_by': 'RANGE (created_at)',
            'listeners': [('after_create', create_user_partition)],
        }
    )

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get('password'))
        self.is_superuser = kwargs.get('is_superuser')

    def __repr__(self):
        return f'User {self.email}'

    @class_tracer(name='Get token')
    def get_token(self):

        additional_claims = {'is_superuser': self.is_superuser}
        access_token = create_access_token(identity=self.id, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=self.id, additional_claims=additional_claims)
        decoded_token = decode_token(refresh_token)

        # Добавляю рефреш токен в БД
        RToken.add(email=self.email, jti=decoded_token['jti'])

        return access_token, refresh_token

    @classmethod
    @class_tracer(name='Authenticate')
    def authenticate(cls, email, password) -> db.Model:
        user = cls.query.filter(cls.email == email).first()
        if user:
            if not bcrypt.verify(password, user.password):
                logger.exception('Invalid password')
                abort(Response(response='Invalid password', status=status.HTTP_401_UNAUTHORIZED))
            return user
        else:
            logger.error('User not found')
            abort(status.HTTP_401_UNAUTHORIZED)

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter(cls.email == email).first()

    def reset(self, **kwargs):
        self.password = bcrypt.hash(kwargs.get('password'))
        db.session.commit()
