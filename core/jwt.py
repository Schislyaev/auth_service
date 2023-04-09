"""
Заготовка для SOLID :)
"""
from flask_jwt_extended import JWTManager
from flask_security import Security, SQLAlchemyUserDatastore

from db.postgres import db
from models.roles import Role
from models.users import User

jwt = JWTManager()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(user_datastore)
