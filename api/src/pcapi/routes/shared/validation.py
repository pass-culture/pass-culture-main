from pydantic.v1 import validator

from pcapi.core.subscription.phone_validation.exceptions import InvalidPhoneNumber
from pcapi.utils import phone_number


def validate_phone_number(number: str | None) -> str:
    try:
        parsed = phone_number.parse_phone_number(number)
    except InvalidPhoneNumber:
        raise ValueError("Ce numéro de telephone ne semble pas valide")
    return phone_number.get_formatted_phone_number(parsed)


def validate_nullable_phone_number(number: str | None) -> str | None:
    if number is None:
        return None

    try:
        parsed = phone_number.parse_phone_number(number)
    except InvalidPhoneNumber:
        raise ValueError("Ce numéro de telephone ne semble pas valide")
    return phone_number.get_formatted_phone_number(parsed)


def phone_number_validator(field_name: str, nullable: bool = False) -> classmethod:
    func = validate_nullable_phone_number if nullable else validate_phone_number
    return validator(field_name, allow_reuse=True)(func)
