from pcapi.connectors import titelive
from pcapi.core.testing import override_settings

from tests.connectors.titelive import fixtures


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
def test_get_jwt(requests_mock):
    requests_mock.post(
        "https://login.epagine.fr/v1/login/test@example.com/token",
        json={"token": "XYZ"},
    )
    assert titelive.get_jwt() == "XYZ"


@override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
@override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
def test_get_by_ean13(requests_mock):
    ean = "9782070455379"
    requests_mock.post(
        "https://login.epagine.fr/v1/login/test@example.com/token",
        json={"token": "XYZ"},
    )
    requests_mock.get(
        f"https://catsearch.epagine.fr/v1/ean/{ean}",
        json=fixtures.EAN_SEARCH_FIXTURE,
    )
    assert titelive.get_by_ean13(ean) == fixtures.EAN_SEARCH_FIXTURE
