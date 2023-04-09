from marshmallow import Schema, fields, validate


class RegistryResponse(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)


class RegistryParams(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True, validate=[validate.Length(min=4, max=60)])
    is_superuser = fields.Boolean(dump_dump_default=False)
