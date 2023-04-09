from dataclasses import dataclass
from http import HTTPStatus

from flask_jwt_extended import decode_token
from flask_sqlalchemy import SQLAlchemy
from jwt.exceptions import InvalidTokenError
from redis import StrictRedis

from core.settings import settings
from db.postgres import db
from db.redis import redis
from grpc_src.messages import permissions_pb2 as permission_messages
from grpc_src.messages import permissions_pb2_grpc as permissions_service
from main import app
from models.endpoints import Endpoint
from models.roles import Role
from models.users import User


@dataclass
class PermissionChecker:
    token: str
    url: str
    db: SQLAlchemy = db
    redis: StrictRedis = redis

    def act(self) -> int:
        is_valid, payload = self.validate_token(self.token)
        if not is_valid:
            return HTTPStatus.UNAUTHORIZED

        if self.check_is_token_blocked(payload['jti']):
            return HTTPStatus.UNAUTHORIZED

        if not self.have_permission(self.url, payload):
            return HTTPStatus.FORBIDDEN

        return HTTPStatus.OK

    @staticmethod
    def validate_token(token: str) -> tuple[bool, dict]:
        try:
            payload = decode_token(token)
        except InvalidTokenError:
            return False, {}

        return True, payload

    def check_is_token_blocked(self, token_id: str) -> bool:
        return self.redis.get(token_id) is not None

    def have_permission(self, url: str, payload: dict) -> bool:
        is_superuser = payload.get('is_superuser')
        if is_superuser:
            return True

        if self.check_permissions_from_cache(user_id=payload['sub'], url=url):
            return True

        return self.check_permission_from_db(user_id=payload['sub'], url=url)

    @staticmethod
    def check_permissions_from_cache(user_id: str, url: str) -> bool:
        accessed_urls_str = redis.get(user_id)
        if accessed_urls_str is None:
            return False

        return url in accessed_urls_str.split(',')

    @staticmethod
    def check_permission_from_db(user_id: str, url: str) -> bool:
        accessed_urls = db.session.query(Endpoint.url) \
                .distinct(Endpoint.url) \
                .join(User.roles, Role.endpoints) \
                .filter(User.id == user_id) \
                .all()
        accessed_urls = [url[0] for url in accessed_urls]

        redis.set(user_id, ','.join(accessed_urls), ex=settings.permission_cache_seconds)

        return url in accessed_urls


class PermissionService(permissions_service.PermissionServicer):
    def CheckPermission(self, request, context):
        with app.app_context():
            service = PermissionChecker(
                token=request.token,
                url=request.url,
            )
            status = service.act()
            return permission_messages.PermissionResponse(status=status)
