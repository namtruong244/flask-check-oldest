from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError


def get_rule():
    return {
        "type": "object",
        "properties": {
            "content": {
                "minLength": 1,
                "maxLength": 4000,
                "type": "string"
            }
        },
        "required": ["content"]
    }


def validate_content(data):
    try:
        validate(data, get_rule())
    except ValidationError as e:
        return {'ok': False, 'message': e.message}
    except SchemaError as e:
        return {'ok': False, 'message': e.message}
    return {'ok': True, 'data': data}
