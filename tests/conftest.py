import json
from http import HTTPStatus

import aiohttp
import pytest
from flask_sqlalchemy import SQLAlchemy

from main import app
from models.users import User

from .settings import test_settings


@pytest.fixture(scope='session')
def connect_postgres():
    db = SQLAlchemy()
    db.init_app(app)
    with app.app_context():
        yield app


@pytest.fixture
def make_http_request():
    async def inner(
            service_path: str,
            method: str = 'GET',
            params: str | None = None,
            data: dict | None = None,
            headers: dict | None = None,
            path: str | None = None,
    ):
        service_url = 'http://{}:{}/api/v1'.format(test_settings.service_url, test_settings.service_port)
        if path:
            url = service_url + service_path + f'/{path}'
        else:
            url = service_url + service_path
        async with aiohttp.request(method=method, url=url, params=params, json=data, headers=headers) as response:
            status = response.status
            if status in [HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.ACCEPTED]:
                body = json.loads(await response.text())
            else:
                body = None
        return {'body': body, 'status': status}

    return inner


@pytest.fixture
def login_user(connect_postgres, make_http_request):
    async def inner_log(
            password: str,
    ):
        postgres_user_email = User.query.order_by(User.created_at.desc()).first()
        data = {
            'email': postgres_user_email.email,
            'password': password,
        }
        user_login = await make_http_request(
            method='POST',
            service_path='/login',
            data=data
        )
        response = user_login['body']
        return response, postgres_user_email.email

    return inner_log
