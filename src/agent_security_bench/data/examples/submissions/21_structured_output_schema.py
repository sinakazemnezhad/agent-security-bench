import json
import jsonschema


def parse_and_validate(raw: str, schema: dict) -> dict:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid json: {exc}") from exc
    try:
        jsonschema.validate(instance=payload, schema=schema)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"schema rejected: {exc.message}") from exc
    return payload
