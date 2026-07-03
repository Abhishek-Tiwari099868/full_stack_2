
from marshmallow import Schema, fields, validate

class UpdateSkillsSchema(Schema):
    skills = fields.List(
        fields.Str(required=True, validate=validate.Length(min=1, max=100)),
        required=True,
        validate=validate.Length(min=0)
    )

class ResumeResponseSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    filename = fields.Str()
    file_url = fields.Str()
    extracted_name = fields.Str(allow_none=True)
    extracted_role = fields.Str(allow_none=True)
    extracted_skills = fields.List(fields.Str())
    analysis = fields.Dict(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
