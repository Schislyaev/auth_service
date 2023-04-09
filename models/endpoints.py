import uuid

from flask import abort
from flask_api import status
from sqlalchemy.dialects.postgresql import UUID

from core.logger import log
from db.postgres import db

logger = log(__name__)


class Endpoint(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String, nullable=False)

    @classmethod
    def add(cls, url):
        try:
            db.session.add(cls(url=url))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.exception(e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def remove(cls, url):
        try:
            cls.query.filter(cls.url == url).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.exception(e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def get(cls, page: int, number: int):
        try:
            page = cls.query.paginate(page=page, per_page=number, error_out=True)
        except Exception as e:
            db.session.rollback()
            logger.exception(e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

        return page
