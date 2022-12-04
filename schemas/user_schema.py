from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError


def get_rule(validate_type):
    rule = {
        "type": "object",
        "properties": {
            "username": {
                "minLength": 5,
                "type": "string",
                "pattern": "^[a-zA-Z0-9]*$"
            },
            "fullname": {
                "minLength": 5,
                "maxLength": 50,
                "type": "string"
            },
            "email": {
                "description": "Email of the user",
                "type": "string",
                "pattern": "^[a-z][a-z0-9_\.]{5,32}@[a-z0-9]{2,}(\.[a-z0-9]{2,4}){1,2}$"
            },
            "password": {
                "description": "Password of the user",
                "minLength": 5,
                "type": "string",
                "pattern": "^[\x00-\x7F]*$"
            }
        },
        "required": ["username", "password"],
        "additionalProperties": False
    }

    if validate_type == "register":
        rule["required"].append("email")

    return rule


def validate_user(data, validate_type):
    try:
        validate(data, get_rule(validate_type))
    except ValidationError as e:
        return {'ok': False, 'message': e.message}
    except SchemaError as e:
        return {'ok': False, 'message': e.message}
    return {'ok': True, 'data': data}
