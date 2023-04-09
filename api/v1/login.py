from json import dumps

from flask import Blueprint, Response
from flask_api import status
from flask_apispec import marshal_with, use_kwargs

from api.schemas.login import LoginParams, LoginResponse
from core.limiter import limiter
from core.logger import log
from services.login import login_and_return_tokens

logger = log(__name__)
login_user = Blueprint('login', __name__)


@login_user.route('/', methods=['POST'])
@use_kwargs(LoginParams)
@marshal_with(LoginResponse)
@limiter.limit('5/minute', error_message='Не спешите, в гости к богу - не бывает опозданий!')
def login(**creds) -> Response:
    tokens = login_and_return_tokens(**creds)
    return Response(response=dumps(tokens), status=status.HTTP_202_ACCEPTED)
