import pytest

from pcapi.connectors import api_adresse
from pcapi.core.testing import override_settings

from tests.connectors.api_adresse import fixtures


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_nominal_case(requests_mock):
    address = "18 Rue Duhesme"
    insee_code = "75118"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.ONE_FEATURE_RESPONSE,
    )
    address_info = api_adresse.get_address(address, city, insee_code)
    assert address_info == api_adresse.AddressInfo(
        id="75118_2974_00018",
        label="18 Rue Duhesme 75018 Paris",
        latitude=2.338562,
        longitude=48.890787,
        score=0.9806027272727271,
    )


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_fallback_to_municipality(requests_mock):
    address = "123456789"
    insee_code = "75118"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search?q=123456789&citycode=75118&autocomplete=0&limit=1",
        json=fixtures.NO_FEATURE_RESPONSE,
    )
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search?q=Paris&citycode=75118&type=municipality&autocomplete=0&limit=1",
        json=fixtures.MUNICIPALITY_CENTROID_RESPONSE,
    )
    address_info = api_adresse.get_address(address, city, insee_code)
    assert address_info == api_adresse.AddressInfo(
        id="75118",
        label="Paris 18e Arrondissement",
        latitude=2.348679,
        longitude=48.892045,
        score=0.2084164031620553,
    )


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_no_match(requests_mock):
    address = "123456789"
    insee_code = "75018"  # not a valid code
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.NO_FEATURE_RESPONSE,
    )
    with pytest.raises(api_adresse.NoResultException):
        api_adresse.get_address(address, city, insee_code)


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (400, api_adresse.InvalidFormatException),
        (429, api_adresse.AdresseApiException),
        (500, api_adresse.AdresseApiException),
        (503, api_adresse.AdresseApiException),
    ],
)
@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_error_handling(status_code, expected_exception, requests_mock):
    address = "invalid"
    insee_code = "75101"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        status_code=status_code,
    )

    with pytest.raises(expected_exception):
        api_adresse.get_address(address, city, insee_code)


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_error_handling_on_non_json_response(requests_mock):
    address = "anything"
    insee_code = "75101"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        status_code=200,
        text="non-JSON content",
    )
    with pytest.raises(api_adresse.AdresseApiException):
        api_adresse.get_address(address, city, insee_code)
