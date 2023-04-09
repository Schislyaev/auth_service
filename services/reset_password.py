from flask import Response, abort
from flask_api import status
from flask_jwt_extended import current_user
from pydantic import ValidationError

from api.v1.schemas.users import UserPasswordModel
from core.logger import log
from services.service import operate_token

logger = log(__name__)


def reset_password_and_get_new_tokens(Authorization: str, password: str) -> dict:
    try:
        validated_password = UserPasswordModel(password=password).password
    except ValidationError as e:
        logger.exception(e)
        abort(Response(e.json(), status=status.HTTP_400_BAD_REQUEST))
    try:
        current_user.reset(password=validated_password)
        access_token, refresh_token = current_user.get_token()
        operate_token(current_user.email, refresh_token)
    except Exception:
        raise
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
