import uuid
from datetime import datetime

from flask import abort
from flask_api import status
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from core.logger import log
from core.tracer.decorators import class_tracer
from db.postgres import db

logger = log(__name__)


class History(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True))
    user_created_at = db.Column(db.DateTime)
    email = db.Column(db.String)
    date = db.Column(db.DateTime)

    __table_args__ = (
        UniqueConstraint('user_id', 'user_created_at'),
        ForeignKeyConstraint(
            ('user_id', 'user_created_at'), ('user.id', 'user.created_at'), ondelete='CASCADE'
        ),
    )

    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.email = kwargs.get('email')
        self.date = datetime.now()

    def __repr__(self):
        return f'{self.email} logged in on {self.date}'

    @classmethod
    @class_tracer(name='Add login history')
    def add(cls, email, user_id):
        try:
            db.session.add(cls(email=email, user_id=user_id))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.exception(e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def get(cls, user_id, page: int = 1, number: int = 30):
        try:
            result = History.query.filter(History.user_id == user_id).paginate(
                page=page,
                per_page=number,
                error_out=True
            )
            return result
        except Exception as e:
            db.session.rollback()
            logger.exception(e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
