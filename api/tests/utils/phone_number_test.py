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
