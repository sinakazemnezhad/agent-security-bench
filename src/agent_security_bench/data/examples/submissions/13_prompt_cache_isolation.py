def cache_key(tenant_id: str, model_id: str, prompt: str) -> str:
    import hashlib

    material = f"{tenant_id}|{model_id}|{prompt}".encode()
    return hashlib.sha256(material).hexdigest()


def get_cached(store, tenant_id: str, model_id: str, prompt: str):
    key = cache_key(tenant_id, model_id, prompt)
    row = store.get(key)
    if row is None:
        return None
    if row.get("tenant_id") != tenant_id:
        raise PermissionError("cross-tenant cache read refused")
    return row["completion"]
