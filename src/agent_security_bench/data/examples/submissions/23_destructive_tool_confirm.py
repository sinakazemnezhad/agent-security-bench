DESTRUCTIVE = frozenset({"delete_all_files", "delete_file", "shell_exec", "drop_table"})


def require_confirmation(tool_name: str, user_message: str, resource_id: str) -> None:
    if tool_name not in DESTRUCTIVE:
        return
    token = f"CONFIRM_DELETE={resource_id}"
    if token not in user_message and f"CONFIRM_{resource_id}" not in user_message:
        raise PermissionError("destructive tool denied: confirmation token missing")
    # confirmation present — caller may proceed
