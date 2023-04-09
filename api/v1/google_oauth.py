from flask import Blueprint, redirect
from flask_apispec import marshal_with

from api.schemas.login import LoginResponse
from core.limiter import limiter
from core.logger import log
from services.google_oauth import authorize, callback

logger = log(__name__)
oauth_google_redirect = Blueprint('google_redirect', __name__)
oauth_google_callback = Blueprint('google_callback', __name__)


@oauth_google_redirect.route('/', methods=['GET'])
@limiter.limit('5/minute')
def google_redirect():
    authorize_url = authorize()
    return redirect(authorize_url, code=302)


@marshal_with(LoginResponse)
@oauth_google_callback.route('/', methods=['GET'])
def google_callback():
    response = callback()
    return response
