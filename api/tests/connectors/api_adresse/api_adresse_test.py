import csv
from io import StringIO
from unittest.mock import patch

import pytest

from pcapi.connectors import api_adresse
from pcapi.core.testing import override_settings

from tests.connectors.api_adresse import fixtures


def test_format_q():
    assert api_adresse.format_q("", "") == " "
    assert api_adresse.format_q("20 Rue Saint-Martin 75004 Paris", "PARIS 4") == "20 Rue Saint-Martin Paris"
    assert api_adresse.format_q(" 33, BD CLEMENCEAU, ", " ,GRENOBLE ") == "33 Boulevard Clemenceau Grenoble"
    assert api_adresse.format_q("105 RUE DES HAIES", "PARIS 20") == "105 Rue Des Haies Paris"


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_nominal_case(requests_mock):
    address = "18 Rue Duhesme"
    postcode = "75018"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.ONE_FEATURE_RESPONSE,
    )
    address_info = api_adresse.get_address(address, postcode, city)
    assert address_info == api_adresse.AddressInfo(
        id="75118_2974_00018",
        label="18 Rue Duhesme 75018 Paris",
        postcode="75018",
        citycode="75118",
        latitude=48.890787,
        longitude=2.338562,
        score=0.9806027272727271,
        street="18 Rue Duhesme",
        city="Paris",
    )


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_fallback_to_municipality(requests_mock):
    address = "123456789"
    postcode = "75018"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search?q=123456789&postcode=75018&autocomplete=0&limit=1",
        json=fixtures.NO_FEATURE_RESPONSE,
    )
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search?q=Paris&postcode=75018&type=municipality&autocomplete=0&limit=1",
        json=fixtures.MUNICIPALITY_CENTROID_RESPONSE,
    )
    address_info = api_adresse.get_address(address, postcode, city)
    assert address_info == api_adresse.AddressInfo(
        id="75118",
        label="Paris 18e Arrondissement",
        postcode="75018",
        citycode="75118",
        latitude=48.892045,
        longitude=2.348679,
        score=0.2084164031620553,
        city="Paris 18e Arrondissement",
    )


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_no_match(requests_mock):
    address = "123456789"
    postcode = "75018"  # not a valid code
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.NO_FEATURE_RESPONSE,
    )
    with pytest.raises(api_adresse.NoResultException):
        api_adresse.get_address(address, postcode, city)


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
    postcode = "75101"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        status_code=status_code,
    )

    with pytest.raises(expected_exception):
        api_adresse.get_address(address, postcode, city)


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_error_handling_on_non_json_response(requests_mock):
    address = "anything"
    postcode = "75101"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        status_code=200,
        text="non-JSON content",
    )
    with pytest.raises(api_adresse.AdresseApiException):
        api_adresse.get_address(address, postcode, city)


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_search_address(requests_mock):
    address = "2 place du carrousel paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.SEARCH_ADDRESS_RESPONSE,
    )
    addresses_info = api_adresse.search_address(address)
    assert len(addresses_info) == 6
    assert addresses_info[0] == api_adresse.AddressInfo(
        id="75101_1578_00002",
        label="2 Place du Carrousel 75001 Paris",
        postcode="75001",
        citycode="75101",
        latitude=48.860255,
        longitude=2.333691,
        score=0.9641372727272727,
        street="2 Place du Carrousel",
        city="Paris",
    )
    assert addresses_info[1] == api_adresse.AddressInfo(
        id="75101_ulje0j",
        label="7S1 Place du Carrousel 75001 Paris",
        postcode="75001",
        citycode="75101",
        latitude=48.861974,
        longitude=2.334394,
        score=0.821388961038961,
        street="7S1 Place du Carrousel",
        city="Paris",
    )


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_search_csv(requests_mock):
    text = api_adresse.format_payload(fixtures.SEARCH_CSV_HEADERS, fixtures.SEARCH_CSV_RESULTS)
    requests_mock.post("https://api-adresse.data.gouv.fr/search/csv", text=text)
    payload = api_adresse.format_payload(fixtures.SEARCH_CSV_HEADERS[:3], fixtures.SEARCH_CSV_RESULTS)
    results = api_adresse.search_csv(
        payload,
        columns=["q"],
        result_columns=[
            api_adresse.ResultColumn.LATITUDE,
            api_adresse.ResultColumn.LONGITUDE,
            api_adresse.ResultColumn.RESULT_ID,
            api_adresse.ResultColumn.RESULT_LABEL,
            api_adresse.ResultColumn.RESULT_SCORE,
        ],
    )
    assert list(results) == list(csv.DictReader(StringIO(text)))


@override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_cache_api(requests_mock):
    payload = {
        "type": "FeatureCollection",
        "version": "draft",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [2.031161, 48.773473]},
                "properties": {
                    "label": "2 Rue de Valois 78180 Montigny-le-Bretonneux",
                    "score": 0.524468831168831,
                    "housenumber": "2",
                    "id": "78423_1855_00002",
                    "name": "2 Rue de Valois",
                    "postcode": "78180",
                    "citycode": "78423",
                    "x": 628801.04,
                    "y": 6853034.12,
                    "city": "Montigny-le-Bretonneux",
                    "context": "78, Yvelines, Île-de-France",
                    "type": "housenumber",
                    "importance": 0.6263,
                    "street": "Rue de Valois",
                },
            }
        ],
        "attribution": "BAN",
        "licence": "ETALAB-2.0",
        "query": "2 rue le valois 7500",
        "limit": 1,
    }
    requests_mock.get("https://api-adresse.data.gouv.fr/search", json=payload)
    api_adresse.get_address(address="3 Rue de Valois 75001 Paris")
    with patch("pcapi.connectors.api_adresse.ApiAdresseBackend._search") as _search_function:
        response = api_adresse.get_address(address="3 Rue de Valois 75001 Paris")
        _search_function.assert_not_called()
        assert response == api_adresse.AddressInfo(
            id="78423_1855_00002",
            label="2 Rue de Valois 78180 Montigny-le-Bretonneux",
            postcode="78180",
            citycode="78423",
            latitude=48.773473,
            longitude=2.031161,
            score=0.524468831168831,
            street="2 Rue de Valois",
            city="Montigny-le-Bretonneux",
        )
