import pytest

from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.utils import phone_number as phone_number_utils


@pytest.mark.parametrize(
    "raw, formatted",
    (
        ("+33102030405", "+33102030405"),
        ("+33102030405 ", "+33102030405"),  # un espace en fin de numéro
        ("+262262161234", "+262262161234"),
        ("0102030405", "+33102030405"),
        ("0262418300", "+262262418300"),
        ("0590860581", "+590590860581"),
        ("0596800070", "+596596800070"),
        ("410200", "+508410200"),
        ("0590278727", "+590590278727"),
        ("0590875721", "+590590875721"),
        ("721717", "+681721717"),
        ("40505700", "+68940505700"),
        ("272727", "+687272727"),
        ("0269635000", "+262269635000"),
        ("0033102030405", "+33102030405"),
    ),
)
def test_parsed_phone_number(raw, formatted):
    parsed_phone_number = phone_number_utils.ParsedPhoneNumber(raw)
    assert parsed_phone_number.phone_number == formatted


@pytest.mark.parametrize(
    "raw, region, formatted",
    (
        ("0102030405", "FR", "+33102030405"),
        ("0033102030405", "FR", "+33102030405"),
        ("0262161234", "RE", "+262262161234"),
    ),
)
def test_parsed_phone_number_region(raw, region, formatted):
    parsed_phone_number = phone_number_utils.ParsedPhoneNumber(raw, region)
    assert parsed_phone_number.phone_number == formatted


@pytest.mark.parametrize(
    "raw, region, formatted",
    (
        ("0102030405", "FR", "+33102030405"),
        ("0033102030405", "FR", "+33102030405"),
        ("0262161234", "RE", "+262262161234"),
    ),
)
def test_parse_phone_number(raw, region, formatted):
    parsed = phone_number_utils.parse_phone_number(raw, region)
    assert phone_number_utils.get_formatted_phone_number(parsed) == formatted


@pytest.mark.parametrize(
    "raw, region",
    (
        (None, "FR"),
        ("+33123", "FR"),
    ),
)
def test_parse_invalid_phone_number(raw, region):
    with pytest.raises(phone_validation_exceptions.InvalidPhoneNumber):
        phone_number_utils.parse_phone_number(raw, region)
