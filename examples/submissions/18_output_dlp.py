import re

SECRET_PATTERNS = [
    r"BEGIN PRIVATE KEY",
    r"Bearer\s+\S+",
    r"sk-[A-Za-z0-9]+",
    r"api_key=",
]


def dlp_gate(text: str) -> str:
    for pat in SECRET_PATTERNS:
        if re.search(pat, text):
            raise ValueError("output blocked by DLP: secret pattern")
    # also refuse token-in-URL style exfil
    if "authorization=" in text.lower() or ".pem" in text.lower():
        return "[redacted]"
    return text
