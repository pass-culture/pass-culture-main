from pydantic.v1 import validator

from pcapi.utils import phone_number as phone_number_utils


def validate_phone_number(number: str | None) -> str:
    try:
        parsed = phone_number_utils.parse_phone_number(number)
    except phone_number_utils.InvalidPhoneNumber:
        raise ValueError("Ce numéro de telephone ne semble pas valide")
    return phone_number_utils.get_formatted_phone_number(parsed)


def validate_nullable_phone_number(number: str | None) -> str | None:
    if number is None:
        return None

    try:
        parsed = phone_number_utils.parse_phone_number(number)
    except phone_number_utils.InvalidPhoneNumber:
        raise ValueError("Ce numéro de telephone ne semble pas valide")
    return phone_number_utils.get_formatted_phone_number(parsed)


def phone_number_validator(field_name: str, nullable: bool = False) -> classmethod:
    func = validate_nullable_phone_number if nullable else validate_phone_number
    return validator(field_name, allow_reuse=True)(func)
