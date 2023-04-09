from marshmallow import Schema, fields, validate


class LoginResponse(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)


class LoginParams(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True, validate=[validate.Length(min=4, max=60)])
