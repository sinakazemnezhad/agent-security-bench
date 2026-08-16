def collection_name(tenant_id: str) -> str:
    if not tenant_id:
        raise PermissionError("tenant_id required for namespace")
    return f"tenant_{tenant_id}"


def upsert(index, tenant_id: str, vectors):
    ns = collection_name(tenant_id)
    return index.upsert(collection=ns, vectors=vectors)


def query(index, tenant_id: str, vector, top_k: int = 5):
    ns = collection_name(tenant_id)
    hits = index.query(collection=ns, vector=vector, top_k=top_k)
    for hit in hits:
        if hit.get("tenant_id") and hit["tenant_id"] != tenant_id:
            raise PermissionError("cross-tenant vector hit refused")
    return hits
