from marshmallow import Schema, fields, validate


class ResetPasswordResponse(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)


class ResetPasswordParams(Schema):
    password = fields.String(required=True, validate=[validate.Length(min=4, max=60)])
