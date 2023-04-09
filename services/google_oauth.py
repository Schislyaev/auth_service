import json
import os
import pathlib
import secrets
import string

import google.auth.transport.requests
from flask import Response
from flask import request as req
from flask_api import status
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from core.settings import settings
from models.login_history import History
from models.users import User
from services.service import create_user, operate_token

client_secrets_file = os.path.join(pathlib.Path(__file__).parent.parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri="http://127.0.0.1:8000/api/oauth/google_callback/")


def authorize():
    authorization_url, state = flow.authorization_url()
    return authorization_url


def callback():
    flow.fetch_token(authorization_response=req.url)
    user_credentials = flow.credentials
    token_request = google.auth.transport.requests.Request()
    user_info = id_token.verify_oauth2_token(
        id_token=user_credentials._id_token,
        request=token_request,
        audience=settings.google_client_id
    )
    user_email = user_info.get("email")

    user_info = User.get_user_by_email(email=user_email)
    if user_info:
        access_token, refresh_token = user_info.get_token()
        History.add(email=user_info.email, user_id=user_info.id)
        operate_token(user_info.email, refresh_token)
        response = Response(json.dumps(
            {
                'access_token': access_token,
                'refresh_token': refresh_token
            }), status=status.HTTP_202_ACCEPTED)
    else:
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(10))
        tokens = create_user(email=user_email, password=password)
        response = Response(json.dumps(tokens), status=status.HTTP_201_CREATED)
    return response
