from marshmallow import Schema, fields


class LoginHistoryResponse(Schema):
    email = fields.Email(required=True)
    login_date = fields.DateTime(required=True)
