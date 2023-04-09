from flask_jwt_extended import (create_access_token, create_refresh_token,
                                current_user, get_jwt, get_jwt_identity)

from services.service import operate_token


def refresh_tokens() -> dict | None:
    try:
        current_user_identity = get_jwt_identity()
        token = get_jwt()

        # создали новые токены
        additional_claims = {'is_superuser': token['is_superuser']}
        refreshed_access_token = create_access_token(
            identity=current_user_identity,
            additional_claims=additional_claims,
            fresh=False
        )
        refreshed_refresh_token = create_refresh_token(
            identity=current_user_identity,
            additional_claims=additional_claims,
        )

        user_email = current_user.email

        operate_token(user_email, token)

    except Exception:
        raise

    return {
        'access_token': refreshed_access_token,
        'refresh_token': refreshed_refresh_token
    }
