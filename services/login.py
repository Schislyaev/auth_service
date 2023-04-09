from flask import abort
from flask_api import status
from pydantic import ValidationError

from api.v1.schemas.users import UserModel
from core.logger import log
from models.login_history import History
from models.users import User
from services.service import operate_token

logger = log(__name__)


def login_and_return_tokens(**creds):
    try:
        validated_user = UserModel(**creds)
    except ValidationError as e:
        logger.exception(e)
        abort(status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = User.authenticate(validated_user.email, validated_user.password)
        access_token, refresh_token = user.get_token()

        History.add(email=user.email, user_id=user.id)

        operate_token(user.email, refresh_token)
    except Exception:
        raise

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
