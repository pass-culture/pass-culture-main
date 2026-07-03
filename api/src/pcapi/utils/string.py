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


def is_numeric(value: str) -> bool:
    # str.isnumeric() and str.isdigit() also accept some characters like '²',
    # str.isdecimal() is more restrictive but accepts unicode characters like '\u0660' (included in r"\d").
    # Regex ensures that value only contains basic digits, so can be a valid integers in database (id, siren, siret...)
    return re.fullmatch(r"[0-9]+", value) is not None


def is_canonical_integer(value: str) -> bool:
    # Regex ensures that value is the canonical representation of an unsigned integer: only basic digits and no leading zeros
    return re.fullmatch(r"0|[1-9][0-9]*", value) is not None


u_nbsp = "\u00a0"
