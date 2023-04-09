from datetime import timedelta

from core.settings import settings


class Config(object):
    DEBUG = True

    SECRET_KEY = settings.flask_app_key
    SECURITY_PASSWORD_SALT = settings.salt

    SQLALCHEMY_DATABASE_URI = settings.database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = settings.jwt_key
    JWT_TOKEN_LOCATION = ['headers']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    OAUTH_CLIENT_ID = settings.google_client_id
    OAUTH_CLIENT_SECRET = settings.google_client_secret

    TRACER = settings.tracer
