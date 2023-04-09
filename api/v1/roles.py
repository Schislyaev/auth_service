import json

from flask import Blueprint, Response
from flask_api import status
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required

from api.schemas.common import TokenHeaders
from api.schemas.roles import (ResponseRolesList, RoleCreateParams,
                               RoleUpdateParams)
from core.logger import log
from services.roles import RolesService
from services.users import is_superuser

logger = log(__name__)
roles = Blueprint('roles', __name__)
service = RolesService()


@roles.route('/', methods=['GET'])
@jwt_required()
@use_kwargs(TokenHeaders, location='headers')
@marshal_with(ResponseRolesList)
@is_superuser()
def get_roles_list(**kwargs) -> Response:
    try:
        results = service.get_list()
        return results.dict()
    except Exception as e:
        logger.exception(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@roles.route('/', methods=['POST'])
@jwt_required()
@use_kwargs(TokenHeaders, location='headers')
@use_kwargs(RoleCreateParams, location='json')
@is_superuser()
def create_role(**kwargs) -> Response | tuple:
    try:
        service.create(kwargs)
        return Response(response=json.dumps({'msg': 'created'}), status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(status=e.code)


@roles.route('/<uuid:id>', methods=['PATCH'])
@jwt_required()
@use_kwargs(TokenHeaders, location='headers')
@use_kwargs(RoleUpdateParams, location='json')
@is_superuser()
def update_role(id, **kwargs) -> Response | tuple:
    try:
        service.update(id, kwargs)
        return Response(response=json.dumps({'msg': 'updated'}), status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(status=e.code)


@roles.route('/<uuid:id>', methods=['DELETE'])
@use_kwargs(TokenHeaders, location='headers')
@jwt_required()
@is_superuser()
def delete_role(id, **kwargs) -> Response | tuple:
    try:
        service.delete(id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response(status=e.code)
