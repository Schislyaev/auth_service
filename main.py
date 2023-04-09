import ast
import json
import os
from http import HTTPStatus as status

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, request
from flask_apispec.extension import FlaskApiSpec
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from werkzeug.exceptions import HTTPException

from api.v1.crud_endpoints import endpoints
from api.v1.google_oauth import oauth_google_callback, oauth_google_redirect
from api.v1.login import login_user
from api.v1.login_history import login_history
from api.v1.logout import logout_user
from api.v1.refresh import refresh_token
from api.v1.register import register_user
from api.v1.reset_password import reset_password
from api.v1.roles import roles
from api.v1.users import edit_user
from core.app_config import Config
from core.commands import user_cli
from core.jwt import jwt, security
from core.limiter import limiter
from core.logger import log
from core.tracer.config import configure_tracer
from db.postgres import db

logger = log(__name__)

app = Flask(__name__)
app.config.from_object(Config)

if app.config.get('TRACER'):
    configure_tracer()
    FlaskInstrumentor.instrument_app(app)


@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('Request id is required')


docs = FlaskApiSpec()

if not os.path.exists("logs/"):
    os.mkdir("logs/")

services = (db, security, jwt, docs) if app.config.get('DEBUG') else (db, security, jwt, docs, limiter)
[service.init_app(app) for service in services]

app.config.update(
    {
        'APISPEC_SPEC': APISpec(
                title='auth_service',
                plugins=[MarshmallowPlugin()],
                openapi_version='2.0',
                version='v1'
            ),
        'APISPEC_SWAGGER_URL': '/swagger/',
    }
)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app.register_blueprint(register_user, url_prefix='/api/v1/register')
app.register_blueprint(login_user, url_prefix='/api/v1/login')
app.register_blueprint(logout_user, url_prefix='/api/v1/logout')
app.register_blueprint(refresh_token, url_prefix='/api/v1/refresh')
app.register_blueprint(reset_password, url_prefix='/api/v1/reset_password')
app.register_blueprint(login_history, url_prefix='/api/v1/login_history')
app.register_blueprint(edit_user, url_prefix='/api/v1/edit_users')
app.register_blueprint(endpoints, url_prefix='/api/v1/endpoints')
app.register_blueprint(roles, url_prefix='/api/v1/roles')
app.register_blueprint(oauth_google_redirect, url_prefix='/api/oauth/google')
app.register_blueprint(oauth_google_callback, url_prefix='/api/oauth/google_callback')


@app.errorhandler(422)
def error_handler(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid request'])
    if headers:
        logger.exception(messages, headers)
        return {'msg': 'Unprocessable Entity'}, status.UNPROCESSABLE_ENTITY, headers
    else:
        logger.exception(messages)
        return {'msg': 'Unprocessable Entity'}, status.UNPROCESSABLE_ENTITY


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    return {'msg': 'Server error'}, status.INTERNAL_SERVER_ERROR


docs.register_existing_resources()

app.cli.add_command(user_cli)

if app.config.get('DEBUG'):
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run()
