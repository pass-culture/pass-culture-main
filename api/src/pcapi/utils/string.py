import re


def to_camelcase(s: str) -> str:
    return re.sub(r"(?!^)_([a-zA-Z])", lambda m: m.group(1).upper(), s)


def is_ean_valid(ean: str) -> bool:
    ean = format_ean_or_visa(ean)
    return ean.isdigit() and len(ean) == 13


def is_visa_valid(visa: str) -> bool:
    visa = format_ean_or_visa(visa)
    return visa.isdigit() and len(visa) <= 10


def format_ean_or_visa(ean: str) -> str:
    return ean.replace("-", "").replace(" ", "")


u_nbsp = "\u00A0"
