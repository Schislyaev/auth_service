from json import dumps

from flask import Blueprint, Response
from flask_api import status
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required

from api.schemas.common import TokenHeaders
from api.schemas.refresh import RefreshResponse
from core.logger import log
from services.refresh import refresh_tokens

logger = log(__name__)
refresh_token = Blueprint('refresh', __name__)


@refresh_token.route('/', methods=['POST'])
@marshal_with(RefreshResponse)
@use_kwargs(TokenHeaders, location='headers')
@jwt_required(refresh=True)
def refresh(**kwargs) -> Response:
    try:
        tokens = refresh_tokens()

    except Exception as e:
        logger.exception(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response=dumps(tokens), status=status.HTTP_200_OK)
