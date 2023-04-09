import json

from flask import Blueprint, Response
from flask_api import status
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required

from api.schemas.common import TokenHeaders
from api.schemas.login_history import LoginHistoryResponse
from core.logger import log
from services.login_history import get_history

logger = log(__name__)
login_history = Blueprint('history', __name__)


@login_history.route('/', methods=['GET'])
@use_kwargs(TokenHeaders, location='headers')
@marshal_with(LoginHistoryResponse(many=True))
@jwt_required()
def history(
        page: int = 1,
        number: int = 30,
        **kwargs
) -> Response:
    try:
        result = get_history(page=page, number=number)

    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response=json.dumps(result), status=status.HTTP_200_OK)
