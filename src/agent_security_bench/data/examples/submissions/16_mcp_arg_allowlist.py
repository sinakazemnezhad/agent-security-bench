ALLOWED = frozenset({"list_dir", "read_file", "http_get"})


def validate_before_dispatch(name: str, arguments: dict, sandbox_root) -> None:
    if name not in ALLOWED:
        raise ValueError(f"tool not on allowlist: {name}")
    if name == "read_file":
        path = (sandbox_root / arguments.get("path", "")).resolve()
        if not path.is_relative_to(sandbox_root.resolve()):
            raise PermissionError("path escapes sandbox")
    if name in {"http_get", "http_post"}:
        url = str(arguments.get("url", "")).lower()
        if "169.254.169.254" in url or "meta-data" in url or "link-local" in url:
            raise ValueError("link-local metadata URL blocked")
