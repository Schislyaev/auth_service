from functools import wraps

from flask import abort, current_app
from flask_jwt_extended import get_jwt

from core.jwt import user_datastore
from core.logger import log
from db.postgres import db
from models.users import User

logger = log(__name__)


def add_roles(Authorization, email, roles):
    try:
        user = User.get_user_by_email(email)
        [user_datastore.add_role_to_user(user, role) for role in roles]
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        logger.exception(e)
        abort(500)


def remove_roles(Authorization, email, roles):
    try:
        user = User.get_user_by_email(email)
        [user_datastore.remove_role_from_user(user, role) for role in roles]
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        logger.exception(e)
        abort(500)


def is_superuser():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            token = get_jwt()
            if not token['is_superuser']:
                abort(403)

            return current_app.ensure_sync(fn)(*args, **kwargs)

        return decorator

    return wrapper
