from marshmallow import Schema, fields


class TypicalResponse(Schema):
    msg = fields.String(required=True)


class TokenHeaders(Schema):
    Authorization = fields.String(required=True,
                                  description='Authorization HTTP header with JWT refresh token, like: Authorization: '
                                              'Bearer asdf.qwer.zxcv')
