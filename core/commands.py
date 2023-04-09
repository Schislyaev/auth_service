import click
from flask.cli import AppGroup

from models.users import User
from services.service import create_user

user_cli = AppGroup('user')


@user_cli.command('create-superuser')
@click.option('--email', help='User email.')
@click.option('--password', help='User passsword.')
def create_superuser(email, password):
    superuser = User(email=email, password=password, is_superuser=True)
    create_user(superuser)
    print('Done!')
