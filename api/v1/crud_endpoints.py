from json import dumps

from flask import Blueprint, Response, request
from flask_api import status
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required

from api.schemas.common import TokenHeaders
from api.schemas.enpoints_crud import CrudEndpointsParams, EndpointElemResponse
from core.logger import log
from services.crud_endpoints import add_urls, get_urls, remove_urls
from services.users import is_superuser

endpoints = Blueprint('crud_endpoints', __name__)
logger = log(__name__)


@endpoints.route('/', methods=['POST', 'GET', 'DELETE'])
@use_kwargs(TokenHeaders, location='headers')
@use_kwargs(CrudEndpointsParams, location='query')
@marshal_with(EndpointElemResponse(many=True))
@jwt_required()
@is_superuser()
def crud_endpoints(
        Authorization,
        urls: list[str | int] | None = None,
        page: int = 1,
        number: int = 30
) -> Response:
    try:
        match request.method:
            case 'POST':
                msg = add_urls(urls)
                http_status = status.HTTP_201_CREATED
            case 'DELETE':
                msg = remove_urls(urls)
                http_status = status.HTTP_200_OK
            case 'GET':
                msg = get_urls(page=page, number=number)
                http_status = status.HTTP_200_OK
    except Exception as e:
        logger.exception(e)
        return Response(response=dumps({'msg': 'Invalid url(s)'}), status=status.HTTP_400_BAD_REQUEST) \
            if str(e) == dumps({'msg': 'Invalid url(s)'}) \
            else Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response=dumps({'msg': msg}), status=http_status)
