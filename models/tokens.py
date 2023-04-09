import uuid

from flask import abort
from flask_api import status
from sqlalchemy.dialects.postgresql import UUID

from core.logger import log
from db.postgres import db

logger = log(__name__)


class RToken(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, nullable=False, unique=False)
    jti = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.jti = kwargs.get('jti')

    def __repr__(self):
        return f'{self.email}'

    @classmethod
    def get_jti(cls, email):
        jti = cls.query.filter(cls.email == email).first()
        return jti.jti

    @classmethod
    def add(cls, email, jti):
        db.session.add(cls(email=email, jti=jti))
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.exception(e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def delete(cls, email):
        try:
            jti_of_rtoken_to_revoke = cls.query.filter(cls.email == email).first()
            cls.query.filter(cls.email == email).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.exception(e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

        return jti_of_rtoken_to_revoke.jti
