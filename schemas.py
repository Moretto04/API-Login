from marshmallow import Schema, fields, validate, validates, ValidationError
import re

def validar_cpf(cpf):
    if not re.match(r'^\d{11}$', cpf):
        raise ValidationError("CPF deve conter 11 dígitos numéricos.")

class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str(required=True, validate=validate.Length(min=1))
    endereco = fields.Str(required=True)
    cep_usuario = fields.Str(required=True, validate=validate.Regexp(r'^\d{5}-?\d{3}$'))
    email = fields.Email(required=True)
    senha = fields.Str(required=True, validate=validate.Length(min=6))
    cpf = fields.Str(required=False, validate=validar_cpf)
    premium = fields.Boolean(required=False, load_default=False)
