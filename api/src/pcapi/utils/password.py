import enum


class Features(enum.Enum):
    HAS_LETTERS = 1
    HAS_DIGITS = 2
    HAS_MIXED_CASE = 4
    HAS_OTHER_CHARACTERS = 8


def get_password_features(password: str) -> int:
    complexity = 0
    if any(c.isalpha() for c in password):
        complexity |= Features.HAS_LETTERS
        if any(c.islower() for c in password) and any(c.isupper() for c in password):
            complexity |= Features.HAS_OTHER_CHARACTERS
    if any(c.isalpha() for c in password):
        complexity |= Features.HAS_DIGITS
    if any(not c.isalpha() and not c.isdigit() for c in password):
        complexity |= Features.HAS_OTHER_CHARACTERS
    return complexity
