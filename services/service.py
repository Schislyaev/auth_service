from typing import Any

from flask import abort
from flask_api import status
from flask_jwt_extended import decode_token
from pydantic import ValidationError

from api.v1.schemas import users
from core.jwt import jwt, user_datastore
from core.logger import log
from core.settings import settings
from core.tracer.decorators import tracer
from db.postgres import db
from db.redis import redis
from models.tokens import RToken
from models.users import User

logger = log(__name__)


def get_and_validate_user(user: users.UserModel) -> User:
    return User(**dict(user))


def create_user(**user_cred) -> dict | None:

    try:
        validated_user = users.UserModel(**user_cred)
    except ValidationError as e:
        logger.exception(e)
        abort(status.HTTP_400_BAD_REQUEST)

    try:
        user = user_datastore.create_user(**validated_user.dict())
        db.session.commit()
        access_token, refresh_token = user.get_token()
    except Exception as e:
        db.session.rollback()
        logger.exception(e)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def put_token_to_blocklist(
        expire,
        token: Any | None = None,
        jti: Any | None = None
):

    if token:
        jti = token["jti"]
        # ttype = token["type"]
    else:
        jti = jti
    try:
        redis.set(jti, "", ex=expire)
    except Exception:
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@tracer(name='Operate token')
def operate_token(user_email, refresh_token):
    try:
        # Удаляю запись токена старого рефреш токена из базы
        jti = RToken.delete(user_email)

        # блоклист рефреша в Redis
        put_token_to_blocklist(expire=settings.access_expires, jti=jti)

        # Записываю новый рефреш в базу
        jti = decode_token(refresh_token)['jti'] if type(refresh_token) is str else refresh_token['jti']
        RToken.add(email=user_email, jti=jti)

    except Exception:
        raise

    return None


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict) -> bool:
    """
    Колбэк функция для отслеживания revoked tokens в Redis.
    Выдает:
    "msg": "Token has been revoked"
    :param jwt_header:
    :param jwt_payload:
    :return: bool
    """
    jti = jwt_payload["jti"]
    token_in_redis = redis.get(jti)
    return token_in_redis is not None


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """
    Колбэк для создания прокси current_user.
    """
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()
