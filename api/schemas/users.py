from marshmallow import Schema, fields


class UsersParams(Schema):
    email = fields.String(required=True)
    roles = fields.List(fields.String, required=True)
