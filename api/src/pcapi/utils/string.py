import re


def to_camelcase(s: str) -> str:
    return re.sub(r"(?!^)_([a-zA-Z])", lambda m: m.group(1).upper(), s)


u_nbsp = "\u00A0"
