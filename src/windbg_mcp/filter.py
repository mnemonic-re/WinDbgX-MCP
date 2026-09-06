"""Filter and redaction engine for sanitizing sensitive paths and secrets in debugger output."""

import re

# Redaction patterns for sensitive information
USER_PROFILE_REGEX = re.compile(r"([A-Za-z]:\\[UsErS|users]+\\)[^\\]+(\\)", re.IGNORECASE)
BEARER_TOKEN_REGEX = re.compile(r"(Bearer\s+)[A-Za-z0-9\-\._~\+\/]+=*", re.IGNORECASE)
API_KEY_REGEX = re.compile(r"(api[_\-]?key|secret|token)\s*[:=]\s*['\"]?([A-Za-z0-9\-\._~]{16,})['\"]?", re.IGNORECASE)
IP_ADDRESS_REGEX = re.compile(r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b")


def sanitize_debug_output(output: str, enable_redaction: bool = True) -> str:
    """Sanitize debugger output logs by removing sensitive paths, tokens, and IP addresses."""
    if not enable_redaction or not output:
        return output

    redacted = USER_PROFILE_REGEX.sub(r"\1[REDACTED_USER]\2", output)
    redacted = BEARER_TOKEN_REGEX.sub(r"\1[REDACTED_TOKEN]", redacted)
    redacted = API_KEY_REGEX.sub(r"\1: [REDACTED_SECRET]", redacted)
    redacted = IP_ADDRESS_REGEX.sub(r"[REDACTED_IP]", redacted)

    return redacted
