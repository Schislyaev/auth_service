from marshmallow import Schema, fields


class RefreshResponse(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
