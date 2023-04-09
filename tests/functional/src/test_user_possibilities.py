import random
import string
from http import HTTPStatus

import pytest

from models.endpoints import Endpoint
from models.login_history import History
from models.roles import Role
from models.tokens import RToken
from models.users import User


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'email': '@mail.ru', 'password': 'mypassword', 'is_superuser': False},
                {'status_code': HTTPStatus.CREATED}
        ),
        (
                {'email': '@mail.ru', 'password': 'mypassword', 'is_superuser': True},
                {'status_code': HTTPStatus.CREATED}
        ),
        (
                {'email': 'ail.ru', 'password': 'mypassword', 'is_superuser': True},
                {'status_code': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
                {'email': '@mail.ru', 'password': 'my', 'is_superuser': True},
                {'status_code': HTTPStatus.UNPROCESSABLE_ENTITY}
        )
    ],
)
@pytest.mark.asyncio
async def test_create_register(
        make_http_request,
        expected_answer,
        query_data,
        connect_postgres
):
    rand_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    user_email = '{}{}'.format(rand_string, query_data['email'])
    data = {
        'email': user_email,
        'password': query_data['password'],
        'is_superuser': query_data['is_superuser']
    }
    new_user_register = await make_http_request(
        method='POST',
        service_path='/register',
        data=data
    )
    postgres_user_record = User.query.filter(User.email == user_email).first()
    postgres_rtoken_record = RToken.query.filter(RToken.email == user_email).first()
    response = new_user_register['body']
    assert new_user_register['status'] == expected_answer['status_code']
    if expected_answer['status_code'] == HTTPStatus.CREATED:
        assert postgres_user_record is not None
        assert postgres_rtoken_record is not None
        assert postgres_user_record.is_superuser == query_data['is_superuser']
        assert response['access_token'] is not None
        assert response['refresh_token'] is not None
    else:
        assert postgres_user_record is None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'email': '', 'password': 'mypassword'},
                {'login_status_code': HTTPStatus.ACCEPTED, 'logout_status_code': HTTPStatus.OK}
        ),
        (
                {'email': 'fake', 'password': 'mypassword'},
                {'login_status_code': HTTPStatus.UNAUTHORIZED}
        ),
        (
                {'email': 'fake', 'password': 'notmypassword'},
                {'login_status_code': HTTPStatus.UNAUTHORIZED}
        ),
    ],
)
@pytest.mark.asyncio
async def test_login_and_logout(
        make_http_request,
        expected_answer,
        query_data,
):
    postgres_user_record = User.query.order_by(User.created_at.desc()).first()
    data = {
        'email': postgres_user_record.email + query_data['email'],
        'password': query_data['password'],
    }
    user_login = await make_http_request(
        method='POST',
        service_path='/login',
        data=data
    )
    postgres_login_history_record = \
        History.query.filter(History.email == postgres_user_record.email + query_data['email']).first()
    response = user_login['body']
    assert user_login['status'] == expected_answer['login_status_code']
    if expected_answer['login_status_code'] != HTTPStatus.ACCEPTED:
        assert postgres_login_history_record is None
    else:
        assert postgres_login_history_record is not None
        assert response['access_token'] is not None
        assert response['refresh_token'] is not None
        user_logout = await make_http_request(
            method='POST',
            service_path='/logout',
            headers={'Authorization': f'Bearer {response["access_token"]}'}
        )
        assert user_logout['body'] is not None
        assert user_logout['status'] == expected_answer['logout_status_code']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'token': '', 'password': 'mypassword'},
                {'status_code': HTTPStatus.OK}
        ),
        (
                {'token': 'add_fake', 'password': 'mypassword'},
                {'status_code': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
    ],
)
@pytest.mark.asyncio
async def test_login_history(
        make_http_request,
        expected_answer,
        query_data,
        login_user
):
    tokens, login_email = await login_user(query_data['password'])
    user_login_history = await make_http_request(
        service_path='/login_history',
        headers={'Authorization': f'Bearer {tokens["access_token"] + query_data["token"]}'}
    )
    assert user_login_history['status'] == expected_answer['status_code']
    if expected_answer['status_code'] == HTTPStatus.OK:
        for login_action in user_login_history['body']:
            assert login_action['email'] == login_email
            assert login_action['login_date'] is not None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'token': '', 'password': 'mypassword'},
                {'status_code': HTTPStatus.OK}
        ),
        (
                {'token': 'fake', 'password': 'mypassword'},
                {'status_code': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_refresh_token(
        make_http_request,
        expected_answer,
        query_data,
        login_user
):
    tokens, login_email = await login_user(query_data['password'])
    old_token_info = RToken.query.filter(RToken.email == login_email).first()

    refresh_token = await make_http_request(
        method='POST',
        service_path='/refresh',
        headers={'Authorization': f'Bearer {tokens["refresh_token"] + query_data["token"]}'}
    )
    assert refresh_token['status'] == expected_answer['status_code']
    if expected_answer['status_code'] == HTTPStatus.OK:
        new_token_info = RToken.query.filter(RToken.email == login_email).first()

        assert new_token_info.id != old_token_info.id
        refresh_token_info = refresh_token['body']
        assert refresh_token_info['access_token'] is not None
        assert refresh_token_info['refresh_token'] is not None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'token': '', 'password': 'mypassword'},
                {'status_code': HTTPStatus.OK}
        ),
        (
                {'token': 'fake', 'password': 'new_password'},
                {'status_code': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_reset_password(
        make_http_request,
        expected_answer,
        query_data,
        login_user,
):
    tokens, login_email = await login_user(query_data['password'])
    reset_password = await make_http_request(
        method='POST',
        service_path='/reset_password',
        data={'password': 'new_password'},
        headers={'Authorization': f'Bearer {tokens["access_token"] + query_data["token"]}'}
    )
    assert reset_password['status'] == expected_answer['status_code']
    if expected_answer['status_code'] == HTTPStatus.OK:
        reset_password_info = reset_password['body']
        assert reset_password_info['access_token'] is not None
        assert reset_password_info['refresh_token'] is not None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'urls': ['https://pypi.org/project/Flask-API/'], 'password': 'new_password'},
                {'record_exist': True, 'post_status_code': HTTPStatus.CREATED, 'get_status_code': HTTPStatus.OK,
                 'delete_status_code': HTTPStatus.OK}
        ),
        (
                {'urls': ['NOT_URL'], 'password': 'new_password'},
                {'record_exist': False, 'post_status_code': HTTPStatus.BAD_REQUEST, 'get_status_code': HTTPStatus.OK,
                 'delete_status_code': HTTPStatus.OK}
        )
    ],
)
@pytest.mark.asyncio
async def test_endpoints_crud(
        make_http_request,
        expected_answer,
        query_data,
        login_user,
):
    tokens, login_email = await login_user(query_data['password'])
    post_endpoint = await make_http_request(
        method='POST',
        service_path='/endpoints',
        params={'urls': query_data['urls']},
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert post_endpoint['status'] == expected_answer['post_status_code']
    endpoint_record = Endpoint.query.filter(Endpoint.url == query_data['urls'][0]).first()

    if expected_answer['record_exist'] is True:
        assert endpoint_record.id is not None
    if expected_answer['record_exist'] is False:
        assert endpoint_record is None
    get_endpoint = await make_http_request(
        method='GET',
        service_path='/endpoints',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert get_endpoint['status'] == expected_answer['get_status_code']
    get_endpoint_info = get_endpoint['body']
    assert get_endpoint_info['msg'] is not None
    delete_endpoint = await make_http_request(
        method='DELETE',
        service_path='/endpoints',
        params={'urls': query_data['urls']},
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert delete_endpoint['status'] == expected_answer['delete_status_code']
    endpoint_record_id = Endpoint.query.filter(Endpoint.url == query_data['urls'][0]).first()

    assert endpoint_record_id is None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'role_name': 'real_role_name', 'password': 'new_password'},
                {'post_status_code': HTTPStatus.CREATED, 'get_status_code': HTTPStatus.OK,
                 'patch_status_code': HTTPStatus.CREATED, 'delete_status_code': HTTPStatus.NO_CONTENT}
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_role_crud(
        make_http_request,
        expected_answer,
        query_data,
        login_user,
):
    tokens, login_email = await login_user(query_data['password'])
    post_endpoint = await make_http_request(
        method='POST',
        service_path='/endpoints',
        params={'urls': ['https://gitlab.com/RuslanPeresy/snippets']},
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert post_endpoint['status'] == HTTPStatus.CREATED
    endpoint_ids = Endpoint.query.first()

    create_data = {
        'name': query_data['role_name'],
        'description': 'descriptions',
        'endpoint_ids': [f'{endpoint_ids.id}']
    }
    create_role = await make_http_request(
        method='POST',
        service_path='/roles',
        data=create_data,
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert create_role['status'] == expected_answer['post_status_code']
    role_record = Role.query.filter(Role.name == query_data['role_name']).first()
    assert role_record is not None
    new_role_name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    patch_data = {
        'name': new_role_name,
        'description': 'other_description',
        'endpoint_ids': [f'{endpoint_ids.id}']
    }
    patch_role = await make_http_request(
        method='PATCH',
        service_path='/roles',
        data=patch_data,
        path=role_record.id,
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert patch_role['status'] == expected_answer['patch_status_code']
    upd_role_record = Role.query.filter(Role.description == 'other_description').first()

    assert upd_role_record.id == role_record.id
    get_role = await make_http_request(
        method='GET',
        service_path='/roles',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    get_role_info = get_role['body']
    assert get_role['status'] == expected_answer['get_status_code']
    assert get_role_info['results'] is not None
    for row in get_role_info['results']:
        assert row['id'] is not None
        assert row['name'] is not None
        assert row['description'] is not None
    delete_role = await make_http_request(
        method='DELETE',
        service_path='/roles',
        path=role_record.id,
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert delete_role['status'] == expected_answer['delete_status_code']
    delete_role_record_info = Role.query.filter(Role.id == role_record.id).first()
    assert delete_role_record_info is None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'email': '', 'password': 'new_password'},
                {'post_status_code': HTTPStatus.CREATED, 'delete_status_code': HTTPStatus.OK}
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_change_role(
        make_http_request,
        expected_answer,
        query_data,
        login_user,
):
    tokens, login_email = await login_user(query_data['password'])
    create_data = {
        'name': 'rolename',
        'description': 'descriptionss',
    }
    _ = await make_http_request(
        method='POST',
        service_path='/roles',
        data=create_data,
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    role_record_id = Role.query.first()
    post_user_role_data = {
        'email': login_email,
        'roles': [role_record_id.name]
    }
    edit_user_role = await make_http_request(
        method='POST',
        service_path='/edit_users',
        data=post_user_role_data,
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert edit_user_role['status'] == expected_answer['post_status_code']
    edit_user_role_info = edit_user_role['body']
    if expected_answer['post_status_code'] == HTTPStatus.OK:
        assert edit_user_role_info['msg'] is not None
    delete_user_role = await make_http_request(
        method='DELETE',
        service_path='/edit_users',
        data=post_user_role_data,
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert delete_user_role['status'] == expected_answer['delete_status_code']
    delete_user_role_info = delete_user_role['body']
    if expected_answer['delete_status_code'] == HTTPStatus.OK:
        assert delete_user_role_info['msg'] is not None
        assert delete_user_role_info['msg'] is not None
