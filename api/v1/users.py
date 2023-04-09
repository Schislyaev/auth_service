from json import dumps

from flask import Blueprint, Response, request
from flask_api import status
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required

from api.schemas.common import TokenHeaders, TypicalResponse
from api.schemas.users import UsersParams
from core.logger import log
from services.users import add_roles, is_superuser, remove_roles

logger = log(__name__)
edit_user = Blueprint('change_users', __name__)


@edit_user.route('/', methods=['POST', 'DELETE'])
@use_kwargs(TokenHeaders, location='headers')
@use_kwargs(UsersParams, location='json')
@marshal_with(TypicalResponse)
@jwt_required()
@is_superuser()
def change_users(**kwargs) -> Response:
    try:
        if request.method == 'POST':
            add_roles(**kwargs)
            http_status = status.HTTP_201_CREATED

        if request.method == 'DELETE':
            remove_roles(**kwargs)
            http_status = status.HTTP_200_OK

    except Exception as e:
        logger.exception(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response=dumps({'msg': 'Success'}), status=http_status)
