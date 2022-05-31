import pytest

from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.utils import phone_number as phone_number_utils


def test_parsed_phone_number():
    parsed_phone_number = phone_number_utils.ParsedPhoneNumber("+33102030405")
    assert parsed_phone_number.phone_number == "+33102030405"

    parsed_phone_number = phone_number_utils.ParsedPhoneNumber(" +33102030405 ")
    assert parsed_phone_number.phone_number == "+33102030405"

    parsed_phone_number = phone_number_utils.ParsedPhoneNumber("+262262161234")
    assert parsed_phone_number.phone_number == "+262262161234"


def test_parsed_phone_number_region():
    parsed_phone_number = phone_number_utils.ParsedPhoneNumber("0102030405", "FR")
    assert parsed_phone_number.phone_number == "+33102030405"

    parsed_phone_number = phone_number_utils.ParsedPhoneNumber("0033102030405", "FR")
    assert parsed_phone_number.phone_number == "+33102030405"

    parsed_phone_number = phone_number_utils.ParsedPhoneNumber("0262161234", "RE")
    assert parsed_phone_number.phone_number == "+262262161234"


def test_parse_phone_number():
    parsed = phone_number_utils.parse_phone_number("06 07 08 09 10", "FR")
    assert phone_number_utils.get_formatted_phone_number(parsed) == "+33607080910"

    parsed = phone_number_utils.parse_phone_number("0607080910", "FR")
    assert phone_number_utils.get_formatted_phone_number(parsed) == "+33607080910"

    parsed = phone_number_utils.parse_phone_number("+39 066 1234567", "FR")
    assert phone_number_utils.get_formatted_phone_number(parsed) == "+390661234567"


def test_parse_invalid_phone_number():
    with pytest.raises(phone_validation_exceptions.InvalidPhoneNumber):
        phone_number_utils.parse_phone_number(None, "FR")

    with pytest.raises(phone_validation_exceptions.InvalidPhoneNumber):
        phone_number_utils.parse_phone_number("+33123", "FR")
