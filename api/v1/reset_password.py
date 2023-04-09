from json import dumps

from flask import Blueprint, Response
from flask_api import status
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required

from api.schemas.common import TokenHeaders
from api.schemas.reset_password import (ResetPasswordParams,
                                        ResetPasswordResponse)
from core.logger import log
from services.reset_password import reset_password_and_get_new_tokens

logger = log(__name__)
reset_password = Blueprint('reset', __name__)


@reset_password.route('/', methods=['POST'])
@marshal_with(ResetPasswordResponse)
@use_kwargs(TokenHeaders, location='headers')
@use_kwargs(ResetPasswordParams, location='json')
@jwt_required()
def reset(**kwargs) -> Response:
    try:
        tokens = reset_password_and_get_new_tokens(**kwargs)

    except Exception as e:
        logger.exception(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response=dumps(tokens), status=status.HTTP_200_OK)
