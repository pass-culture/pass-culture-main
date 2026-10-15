"""Best-effort removal of personal data from free text before it is sent to the LLM.

Regexes cannot catch everything (people names for instance): the widget also
tells users not to type personal data.
"""

import re


# Order matters: the most specific patterns must run first (an IBAN contains
# digit sequences that would otherwise be caught by the SIRET/card patterns, a
# SIRET is a 14 digits sequence that would otherwise be caught by the card pattern).
_REDACTION_PATTERNS: tuple[tuple[str, re.Pattern], ...] = (
    ("[EMAIL]", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.IGNORECASE)),
    ("[URL]", re.compile(r"\bhttps?://\S+", re.IGNORECASE)),
    ("[IBAN]", re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,4})?\b", re.IGNORECASE)),
    # SIRET (14 digits) and SIREN (9 digits), possibly grouped by spaces
    ("[SIRET]", re.compile(r"\b\d{3}[ ]?\d{3}[ ]?\d{3}[ ]?\d{5}\b")),
    ("[SIREN]", re.compile(r"\b\d{3}[ ]?\d{3}[ ]?\d{3}\b")),
    # Card numbers: 13 to 19 digits, possibly grouped by spaces or dashes
    ("[CARTE]", re.compile(r"\b\d{4}(?:[ -]?\d{4}){2}[ -]?\d{1,7}\b")),
    # French phone numbers: 0X XX XX XX XX, +33 X XX XX XX XX, with optional separators
    ("[TELEPHONE]", re.compile(r"(?:(?:\+|00)33[ .-]?|\b0)[1-9](?:[ .-]?\d{2}){4}\b")),
    # Countermarks (booking tokens): 6 uppercase alphanumeric chars with at least one digit and one letter
    ("[CONTREMARQUE]", re.compile(r"\b(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{6}\b")),
)


def redact(text: str) -> str:
    for placeholder, pattern in _REDACTION_PATTERNS:
        text = pattern.sub(placeholder, text)
    return text
