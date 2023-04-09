from marshmallow import Schema, fields


class CrudEndpointsParams(Schema):
    urls = fields.List(fields.String, dump_dump_default=None)


class EndpointElemResponse(Schema):
    id = fields.UUID(required=True)
    url = fields.Url(required=True)
