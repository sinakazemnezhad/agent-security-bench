import re


def sanitize_retrieved_html(doc: str) -> str:
    # Strip HTML comments that may carry prompt-injection tool directives.
    cleaned = re.sub(r"<!--.*?-->", "", doc, flags=re.DOTALL)
    cleaned = re.sub(r"</?policy_override[^>]*>", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()
