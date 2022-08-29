import enum

import phonenumbers
from phonenumbers import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException

from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions


class EligibleRegions(enum.Enum):
    GP = "GP"  # Guadeloupe  (+590)
    MQ = "MQ"  # Martinique (+596)
    GF = "GF"  # Guyane (+594)
    RE = "RE"  # Réunion (+262)
    PM = "PM"  # Saint Pierre et Miquelon (+508)
    YT = "YT"  # Mayotte (+262)
    FR = "FR"  # métropole (+33)


class ParsedPhoneNumber:
    def __init__(self, base_phone_number: str, region: str | None = None):
        self.parsed_phone_number = parse_phone_number(base_phone_number, region)
        self.phone_number = get_formatted_phone_number(self.parsed_phone_number)
        self.country_code = self.parsed_phone_number.country_code


def parse_phone_number(phone_number: str | None, region: str | None = None) -> PhoneNumber:
    """
    Phone number must be correctly formatted in international format (E.164)
    and be valid (number of digits, digit sequence)

    Raises:
        InvalidPhoneNumber
    """
    if phone_number is None:
        raise phone_validation_exceptions.InvalidPhoneNumber

    regions = tuple(EligibleRegions) if region is None else (getattr(EligibleRegions, region),)
    parsed_phone_number = None
    for r in regions:
        try:
            parsed_phone_number = phonenumbers.parse(phone_number, r.value)
        except NumberParseException:
            pass
        except TypeError as err:
            raise phone_validation_exceptions.InvalidPhoneNumber(str(phone_number)) from err
        else:
            if phonenumbers.is_valid_number(parsed_phone_number):
                break

            parsed_phone_number = None

    if parsed_phone_number is None:
        raise phone_validation_exceptions.InvalidPhoneNumber(
            f"provided phone number ({phone_number}) does not belong to an eligible region ({regions})"
        )

    return parsed_phone_number


def get_formatted_phone_number(phone_number: PhoneNumber) -> str:
    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
