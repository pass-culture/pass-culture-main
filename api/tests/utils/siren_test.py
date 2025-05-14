import pytest

from pcapi.utils import siren as siren_utils


@pytest.mark.parametrize(
    "digits,expected",
    [
        ("73282932", "732829320"),
        ("85331845", "853318459"),
        ("8533184590001", "85331845900015"),
        ("8533184590002", "85331845900023"),
        ("8533184590003", "85331845900031"),
        ("8533184590004", "85331845900049"),
        ("11004601", "110046018"),
        ("1100460180001", "11004601800013"),
        ("12345678", "123456782"),
    ],
)
def test_complete_siren_or_siret(digits, expected):
    result = siren_utils.complete_siren_or_siret(digits)
    assert result == expected


@pytest.mark.parametrize(
    "digits,expected",
    [
        ("732829320", True),
        ("853318459", True),
        ("85331845", False),
        ("8533184590", False),
        ("110046018", True),
        ("110046019", False),
        ("110046018 ", False),
        ("notasiren", False),
    ],
)
def test_is_valid_siren(digits, expected):
    result = siren_utils.is_valid_siren(digits)
    assert result == expected


@pytest.mark.parametrize(
    "digits,expected",
    [
        ("85331845900015", True),
        ("853318459000155", False),
        ("85331845900022", False),
        ("1100460180001", False),
        ("11004601800018", False),
        ("11004601800013", True),
        ("11004601800013 ", False),
        ("invalid__siret", False),
        ("35600000000048", True),  # La Poste
        ("35600000009075", True),  # La Poste
    ],
)
def test_is_valid_siret(digits, expected):
    result = siren_utils.is_valid_siret(digits)
    assert result == expected


@pytest.mark.parametrize(
    "data,expected",
    [("NC1234567", True), ("NN1234567", False), ("123456789", False), ("NCNCNCNCN", False)],
)
def test_is_rid7(data, expected):
    result = siren_utils.is_rid7(data)
    assert result == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ("NC1234567001XX", True),
        ("NC1234567001", False),
        ("NN1234567890XX", False),
        (None, False),
    ],
)
def test_is_ridet(data, expected):
    result = siren_utils.is_ridet(data)
    assert result == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ("12345678900012", True),
        ("123456789", False),
        ("NC1234567001XX", True),
        ("NC1234567001", False),
        ("NN1234567890XX", False),
    ],
)
def test_is_ridet_or_siret(data, expected):
    result = siren_utils.is_siret_or_ridet(data)
    assert result == expected


def test_siren_to_rid7():
    result = siren_utils.siren_to_rid7("NC1234567")
    assert result == "1234567"


def test_rid7_to_siren():
    result = siren_utils.rid7_to_siren("1234567")
    assert result == "NC1234567"


def test_siret_to_ridet():
    result = siren_utils.siret_to_ridet("NC1234567001XX")
    assert result == "1234567001"


def test_ridet_to_siret():
    result = siren_utils.ridet_to_siret("1234567001")
    assert result == "NC1234567001XX"
