from typing import Optional

import phonenumbers
from phonenumbers import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException

from pcapi.core.users.exceptions import InvalidPhoneNumber


class ParsedPhoneNumber:
    def __init__(self, base_phone_number: str, region: Optional[str] = None):
        self.parsed_phone_number = parse_phone_number(base_phone_number, region)
        self.phone_number = get_formatted_phone_number(self.parsed_phone_number)
        self.country_code = self.parsed_phone_number.country_code


def parse_phone_number(phone_number: Optional[str], region: Optional[str] = None) -> PhoneNumber:
    """
    Phone number must be correctly formatted in international format (E.164)
    and be valid (number of digits, digit sequence)

    Raises:
        InvalidPhoneNumber
    """
    try:
        if region:
            parsed_phone_number = phonenumbers.parse(phone_number, region)
        else:
            parsed_phone_number = phonenumbers.parse(phone_number)
    except NumberParseException as error:
        raise InvalidPhoneNumber(str(phone_number)) from error
    except TypeError as error:
        raise InvalidPhoneNumber(str(phone_number)) from error

    if not phonenumbers.is_valid_number(parsed_phone_number):
        raise InvalidPhoneNumber(str(phone_number))

    return parsed_phone_number


def get_formatted_phone_number(phone_number: PhoneNumber) -> str:
    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
