"""Domain containment filter to reject non-HR queries."""
import re
from typing import Tuple

OUT_OF_DOMAIN_PATTERNS = [
    r"\b(write|create|code|debug)\s+(a\s+)?(python|javascript|java|c\+\+|rust|go|sql)\s+(function|script|code|algorithm|program)",
    r"\bsort\s+a\s+list\s+of\s+numbers\b",
    r"\bwrite\s+a\s+(poem|essay|story|song)\b",
    r"\bwho\s+won\s+the\s+(world\s+cup|super\s+bowl|election)\b",
    r"\bwhat\s+is\s+the\s+capital\s+of\b",
    r"\bpet('s)?\s+(birthday|party)\b",
]

COMPILED_OOD_REGEX = re.compile("|".join(OUT_OF_DOMAIN_PATTERNS), re.IGNORECASE)

OOD_REFUSAL_MESSAGE = (
    "I could not find an answer to this in our approved HR policy documents. "
    "Please contact the HR Direct support desk for further assistance."
)


def inspect_domain_containment(prompt: str) -> Tuple[bool, str]:
    """Check if query is out of the enterprise HR domain.
    
    Returns:
        (is_in_domain: bool, message: str)
    """
    if COMPILED_OOD_REGEX.search(prompt):
        return False, OOD_REFUSAL_MESSAGE
    return True, ""
