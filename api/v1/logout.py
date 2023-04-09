from json import dumps

from flask import Blueprint, Response
from flask_api import status
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required

from api.schemas.common import TokenHeaders, TypicalResponse
from core.logger import log
from services.logout import revoke_token_and_delete_rtoken_from_db

logger = log(__name__)
logout_user = Blueprint('logout', __name__)


@logout_user.route('/', methods=['POST'])
@marshal_with(TypicalResponse)
@use_kwargs(TokenHeaders, location='headers')
@jwt_required()
def logout(**kwargs) -> Response:

    try:
        revoke_token_and_delete_rtoken_from_db()
    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response=dumps({'msg': 'logged out'}), status=status.HTTP_200_OK)
