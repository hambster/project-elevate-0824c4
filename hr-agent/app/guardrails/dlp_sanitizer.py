"""Cloud DLP / Regex Ephemeral SPII and Secret Masker."""
import re
from typing import Tuple

# SSN: 3 digits - 2 digits - 4 digits
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
# Password patterns
PASSWORD_REGEX = re.compile(r"(?:password\s+is\s+|corporate\s+password\s+is\s+)([A-Za-z0-9!@#$%^&*()_+=\-]{6,})", re.IGNORECASE)


def sanitize_input(text: str) -> str:
    """Mask SSNs and cleartext passwords with standard DLP tokens."""
    sanitized = SSN_REGEX.sub("[REDACTED_SSN]", text)
    sanitized = PASSWORD_REGEX.sub(r"password is [REDACTED_SECRET]", sanitized)
    return sanitized
