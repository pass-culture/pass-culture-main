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
