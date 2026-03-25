import enum

import phonenumbers
from phonenumbers import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException

from pcapi import settings


class EligibleRegions(enum.Enum):
    GP = "GP"  # Guadeloupe  (+590)
    MQ = "MQ"  # Martinique (+596)
    GF = "GF"  # Guyane (+594)
    RE = "RE"  # Réunion (+262)
    PM = "PM"  # Saint Pierre et Miquelon (+508)
    YT = "YT"  # Mayotte (+262)
    BL = "BL"  # Saint Barthélémy (+590)
    MF = "MF"  # Saint Martin (+590)
    WF = "WF"  # Wallis et Futuna (+681)
    PF = "PF"  # Polynésie française (+689)
    NC = "NC"  # Nouvelle Calédonie (+687)
    FR = "FR"  # métropole (+33)


WHITELISTED_COUNTRY_PHONE_CODES = {
    33,  # France métropolitaine
    262,  # Réunion and Mayotte
    508,  # Saint-Pierre-et-Miquelon
    590,  # Guadeloupe, Saint-Barthélémy and Saint-Martin
    594,  # Guyane
    596,  # Martinique
    681,  # Wallis-et-Futuna
    687,  # Nouvelle-Calédonie
    689,  # Tahiti
}


class PhoneVerificationException(Exception):
    pass


class RequiredPhoneNumber(PhoneVerificationException):
    pass


class InvalidPhoneNumber(PhoneVerificationException):
    pass


class InvalidCountryCode(InvalidPhoneNumber):
    pass


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
        raise InvalidPhoneNumber

    regions = tuple(EligibleRegions) if region is None else (getattr(EligibleRegions, region),)
    parsed_phone_number = None
    for r in regions:
        try:
            parsed_phone_number = phonenumbers.parse(phone_number, r.value)
        except NumberParseException:
            pass
        except TypeError as err:
            raise InvalidPhoneNumber(str(phone_number)) from err
        else:
            if phonenumbers.is_valid_number(parsed_phone_number):
                break

            parsed_phone_number = None

    if parsed_phone_number is None:
        raise InvalidPhoneNumber(
            f"provided phone number ({phone_number}) does not belong to an eligible region {tuple(r.value for r in regions)}"
        )
    return parsed_phone_number


def get_formatted_phone_number(phone_number: PhoneNumber) -> str:
    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)


def check_phone_number_is_legit(phone_number: str, country_code: int | None) -> None:
    if phone_number in settings.BLACKLISTED_SMS_RECIPIENTS:
        raise InvalidPhoneNumber()

    if country_code not in WHITELISTED_COUNTRY_PHONE_CODES:
        raise InvalidCountryCode()
