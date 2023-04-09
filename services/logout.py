from flask_jwt_extended import current_user, get_jwt

from core.settings import settings
from db.redis import redis
from models.tokens import RToken


def revoke_token_and_delete_rtoken_from_db():
    try:
        pipline = redis.pipeline()

        # revoke access token
        access_jti = get_jwt()['jti']
        pipline.set(access_jti, '', ex=settings.access_expires)

        # revoke refresh token
        email = current_user.email
        refresh_jti = RToken.get_jti(email)
        pipline.set(refresh_jti, '', ex=settings.refresh_expires)

        pipline.execute()

        # удаляем refresh из postgres
        RToken.delete(email)

    except Exception:
        raise
