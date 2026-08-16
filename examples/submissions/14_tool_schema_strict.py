import jsonschema


ALLOWLIST = {"list_dir", "read_file"}


def invoke_tool(name: str, arguments: dict, schemas: dict):
    if name not in ALLOWLIST:
        raise ValueError(f"unknown tool not allowlisted: {name}")
    schema = schemas[name]
    jsonschema.validate(instance=arguments, schema=schema)
    return dispatch(name, arguments)
