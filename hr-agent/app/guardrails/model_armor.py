"""Model Armor pre-execution prompt injection and jailbreak filter (<150ms)."""
import re
from typing import Tuple

# Known prompt injection & jailbreak patterns
INJECTION_PATTERNS = [
    r"ignore\s+all\s+(previous\s+)?instructions",
    r"output\s+the\s+system\s+prompt",
    r"system\s+prompt\s+verbatim",
    r"dan\s+mode",
    r"do\s+anything\s+now",
    r"bypass\s+all\s+safety",
    r"reveal\s+(all\s+)?secret\s+keys",
    r"extract\s+all\s+employee\s+salaries",
    r"act\s+as\s+an\s+unrestricted",
    r"developer\s+mode\s+enabled",
    r"you\s+are\s+now\s+in\s+god\s+mode",
]

COMPILED_INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)

SAFETY_REFUSAL_MESSAGE = (
    "I cannot process this request as it violates company AI safety policies. "
    "Please rephrase your question regarding HR policies or self-service."
)


def inspect_prompt_safety(prompt: str) -> Tuple[bool, str]:
    """Inspect query for prompt injection and jailbreaks.
    
    Returns:
        (is_safe: bool, message: str)
    """
    if COMPILED_INJECTION_REGEX.search(prompt):
        return False, SAFETY_REFUSAL_MESSAGE
    return True, ""
