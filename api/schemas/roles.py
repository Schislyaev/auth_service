from marshmallow import Schema, fields


class RoleCreateParams(Schema):
    name = fields.String(required=True)
    description = fields.String(dump_dump_default='')
    endpoint_ids = fields.List(fields.String, dump_dump_default=[])


class RoleUpdateParams(Schema):
    name = fields.String(dump_dump_default=None)
    description = fields.String(dump_dump_default=None)
    endpoint_ids = fields.List(fields.String, dump_dump_default=None)


class RoleInformation(Schema):
    id = fields.UUID(required=True)
    description = fields.String(required=True)
    name = fields.String()


class ResponseRolesList(Schema):
    results = fields.List(fields.Nested(RoleInformation), required=True)
