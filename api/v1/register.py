from http import HTTPStatus
from json import dumps

from flask import Blueprint, Response, abort
from flask_api import status
from flask_apispec import marshal_with, use_kwargs

from api.schemas.registry import RegistryParams, RegistryResponse
from core.limiter import limiter
from core.logger import log
from services.service import create_user

logger = log(__name__)
register_user = Blueprint('register', __name__)


@register_user.route('/', methods=['POST'])
@marshal_with(RegistryResponse)
@use_kwargs(RegistryParams, location='json')
@limiter.limit('5/30second', error_message='Не спешите, в гости к богу - не бывает опозданий!')
def register(**kwargs) -> Response | None:
    try:
        msg = create_user(**kwargs)
    except Exception as e:
        if e.code in range(400, 500):
            abort(Response(status=HTTPStatus.UNPROCESSABLE_ENTITY))
        abort(Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR))

    return Response(response=dumps(msg), status=status.HTTP_201_CREATED)
