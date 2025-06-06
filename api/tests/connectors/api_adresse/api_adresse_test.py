import csv
import json
from hashlib import md5
from io import StringIO
from unittest.mock import call
from unittest.mock import patch

import pytest

from pcapi.connectors import api_adresse

from tests.connectors.api_adresse import fixtures


def test_format_q():
    assert api_adresse.format_q("", "") == " "
    assert api_adresse.format_q("20 Rue Saint-Martin 75004 Paris", "PARIS 4") == "20 Rue Saint-Martin Paris"
    assert api_adresse.format_q(" 33, BD CLEMENCEAU, ", " ,GRENOBLE ") == "33 Boulevard Clemenceau Grenoble"
    assert api_adresse.format_q("105 RUE DES HAIES", "PARIS 20") == "105 Rue Des Haies Paris"


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_nominal_case(requests_mock):
    address = "18 Rue Duhesme"
    postcode = "75018"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search?q=18+Rue+Duhesme&postcode=75018&city=Paris&autocomplete=0&limit=1",
        json=fixtures.ONE_FEATURE_RESPONSE,
    )
    address_info = api_adresse.get_address(address, postcode=postcode, city=city)
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


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
@pytest.mark.parametrize("address", ['"18 Rue Duhesme"', "« 18 Rue Duhesme »", "“18 Rue Duhesme”", "'18 Rue Duhesme'"])
def test_with_quotes(requests_mock, address):
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search?q=18+Rue+Duhesme&postcode=75018&city=Paris&autocomplete=0&limit=1",
        json=fixtures.ONE_FEATURE_RESPONSE,
    )
    api_adresse.get_address(address, postcode="75018", city="Paris")
    assert requests_mock.call_count == 1


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_municipality_centroid_with_city_less_than_3_characters(requests_mock):
    postcode = "80190"
    city = "Y"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search?q=80190+Y&postcode=80190&type=municipality&autocomplete=0&limit=1",
        json=fixtures.ONE_MUNICIPALITY_CENTROID_RESPONSE_CITY_NAME_LESS_THAN_3_CHARS,
    )
    address_info = api_adresse.get_municipality_centroid(city=city, postcode=postcode)
    assert address_info == api_adresse.AddressInfo(
        id="80829",
        label="Y",
        postcode="80190",
        citycode="80829",
        latitude=49.803313,
        longitude=2.991219,
        score=0.924650909090909,
        city="Y",
        street="Y",
    )


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
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
    address_info = api_adresse.get_address(address, postcode=postcode, city=city)
    assert address_info == api_adresse.AddressInfo(
        id="75118",
        label="Paris 18e Arrondissement",
        postcode="75018",
        citycode="75118",
        latitude=48.892045,
        longitude=2.348679,
        score=0.2084164031620553,
        city="Paris 18e Arrondissement",
        street="Paris 18e Arrondissement",
    )


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_no_match(requests_mock):
    address = "123456789"
    postcode = "75018"  # not a valid code
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.NO_FEATURE_RESPONSE,
    )
    with pytest.raises(api_adresse.NoResultException):
        api_adresse.get_address(address, postcode=postcode, city=city)


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_should_raise_if_strict_is_set_to_true_and_score_is_below_RELIABLE_SCORE_THRESHOLD(requests_mock):
    address = "123456789"
    postcode = "75018"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.ONE_UNRELIABLE_FEATURE_RESPONSE,
    )
    with pytest.raises(api_adresse.NoResultException):
        api_adresse.get_address(address, postcode=postcode, city=city, strict=True)


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_should_not_fallback_to_municipality_if_strict_is_set_to_true(requests_mock):
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
    with pytest.raises(api_adresse.NoResultException):
        api_adresse.get_address(address, postcode=postcode, city=city, strict=True)


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (400, api_adresse.InvalidFormatException),
        (429, api_adresse.AdresseApiException),
        (500, api_adresse.AdresseApiException),
        (503, api_adresse.AdresseApiException),
    ],
)
@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_error_handling(status_code, expected_exception, requests_mock):
    address = "invalid"
    postcode = "75101"
    city = "Paris"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        status_code=status_code,
    )

    with pytest.raises(expected_exception):
        api_adresse.get_address(address, postcode=postcode, city=city)


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
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
        api_adresse.get_address(address, postcode=postcode, city=city)


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
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


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def test_search_address_without_postcode(requests_mock):
    address = "Stephen Atwater Saint Barthelemy"
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search",
        json=fixtures.SEARCH_ADDRESS_RESPONSE_WITHOUT_POSTCODE,
    )
    addresses_info = api_adresse.search_address(address)
    assert addresses_info == [
        api_adresse.AddressInfo(
            id="97701_h9kt3t",
            label="Rue Stephen Atwater Saint-Barthélemy",
            postcode="97133",
            citycode="97701",
            latitude=17.897144,
            longitude=-62.851796,
            score=0.6843390909090907,
            street="Rue Stephen Atwater",
            city="Saint-Barthélemy",
        )
    ]


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
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


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
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


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
@patch(
    "pcapi.connectors.api_adresse.ApiAdresseBackend._search",
    side_effect=[
        {"type": "FeatureCollection", "features": []},  # Falsy empty response when querying the address
        {
            "type": "FeatureCollection",
            "version": "draft",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [2.347, 48.859]},
                    "properties": {
                        "label": "Paris",
                        "score": 0.10937561497326202,
                        "id": "75056",
                        "type": "municipality",
                        "name": "Paris",
                        "postcode": "75001",
                        "citycode": "75056",
                        "x": 652089.7,
                        "y": 6862305.26,
                        "population": 2133111,
                        "city": "Paris",
                        "context": "75, Paris, Île-de-France",
                        "importance": 0.67372,
                        "municipality": "Paris",
                    },
                }
            ],
            "attribution": "BAN",
            "licence": "ETALAB-2.0",
            "query": "3 Rue de Valois",
            "filters": {"postcode": "75001", "type": "municipality"},
            "limit": 1,
        },  # Connector falling back on the centroid
    ],
)
@patch("flask.current_app.redis_client.delete")
@patch("flask.current_app.redis_client.set", side_effect=[None, None])
@patch("flask.current_app.redis_client.get", side_effect=[None, None])
def test_we_dont_cache_falsy_empty_response(mocked_redis_get, mocked_redis_set, mocked_redis_delete, mocked_search):
    payload = {
        "q": "3 Rue de Valois",
        "postcode": "75001",
        "citycode": None,
        "city": "Paris",
        "autocomplete": 0,
        "limit": 1,
    }
    response = api_adresse.get_address(address="3 Rue de Valois", postcode="75001", city="Paris")
    address_cache_key = f"cache:api:addresse:search:{md5(json.dumps(payload).encode()).hexdigest()}"
    centroid_cache_key = f"cache:api:addresse:search:{md5(json.dumps({'q': 'Paris', 'postcode': '75001', 'citycode': None, 'type': 'municipality', 'autocomplete': 0, 'limit': 1}).encode()).hexdigest()}"

    ### redis_client.get calls ###
    get_calls = [call(address_cache_key), call(centroid_cache_key)]
    mocked_redis_get.assert_has_calls(get_calls)

    ### redis_client.set calls ###
    set_calls = [
        call(address_cache_key, json.dumps({"type": "FeatureCollection", "features": []}).encode(), ex=86400 * 7),
        call(
            centroid_cache_key,
            json.dumps(
                {
                    "type": "FeatureCollection",
                    "version": "draft",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [2.347, 48.859]},
                            "properties": {
                                "label": "Paris",
                                "score": 0.10937561497326202,
                                "id": "75056",
                                "type": "municipality",
                                "name": "Paris",
                                "postcode": "75001",
                                "citycode": "75056",
                                "x": 652089.7,
                                "y": 6862305.26,
                                "population": 2133111,
                                "city": "Paris",
                                "context": "75, Paris, Île-de-France",
                                "importance": 0.67372,
                                "municipality": "Paris",
                            },
                        }
                    ],
                    "attribution": "BAN",
                    "licence": "ETALAB-2.0",
                    "query": "3 Rue de Valois",
                    "filters": {"postcode": "75001", "type": "municipality"},
                    "limit": 1,
                }
            ).encode(),
            ex=86400 * 7,
        ),
    ]
    mocked_redis_set.assert_has_calls(set_calls)  # Wrongly caching the response

    ### redis_client.delete calls ###
    mocked_redis_delete.assert_called_with(
        address_cache_key
    )  #  Ensure we don’t serve the wrongly empty response for others users

    ### Ensure we don’t break anything from the BAN API connector ###
    assert (
        mocked_search.call_count == 2
    )  # Searching the address, BAN API return wrongly an empty response, then falling back on asking for the centroid
    mocked_search.assert_any_call(
        {"q": "3 Rue de Valois", "postcode": "75001", "citycode": None, "city": "Paris", "autocomplete": 0, "limit": 1}
    )
    mocked_search.assert_any_call(
        {"q": "Paris", "postcode": "75001", "citycode": None, "type": "municipality", "autocomplete": 0, "limit": 1}
    )  # Connector fallback on the centroid because the `get_single_address_result` returned (falsy) empty
    assert response == api_adresse.AddressInfo(
        id="75056",
        label="Paris",
        postcode="75001",
        citycode="75056",
        latitude=48.859,
        longitude=2.347,
        score=0.10937561497326202,
        street="Paris",
        city="Paris",
    )


@pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
@patch(
    "pcapi.connectors.api_adresse.ApiAdresseBackend._search",
    side_effect=[
        {"type": "FeatureCollection", "features": []},  # Falsy empty response when querying the address
        {"type": "FeatureCollection", "features": []},  # Falsy empty response when falling back on the centroid
    ],
)
@patch("flask.current_app.redis_client.delete")
@patch("flask.current_app.redis_client.set", side_effect=[None, None])
@patch("flask.current_app.redis_client.get", side_effect=[None, None])
def test_we_dont_cache_falsy_empty_response_when_falling_back_on_centroid(
    mocked_redis_get, mocked_redis_set, mocked_redis_delete, mocked_search
):
    payload = {
        "q": "3 Rue de Valois",
        "postcode": "75001",
        "citycode": None,
        "city": "Paris",
        "autocomplete": 0,
        "limit": 1,
    }
    with pytest.raises(api_adresse.NoResultException):
        api_adresse.get_address(address="3 Rue de Valois", postcode="75001", city="Paris")
    address_cache_key = f"cache:api:addresse:search:{md5(json.dumps(payload).encode()).hexdigest()}"
    centroid_cache_key = f"cache:api:addresse:search:{md5(json.dumps({'q': 'Paris', 'postcode': '75001', 'citycode': None, 'type': 'municipality', 'autocomplete': 0, 'limit': 1}).encode()).hexdigest()}"

    ### redis_client.get calls ###
    get_calls = [call(address_cache_key), call(centroid_cache_key)]
    mocked_redis_get.assert_has_calls(get_calls)

    ### redis_client.set calls ###
    set_calls = [
        call(address_cache_key, json.dumps({"type": "FeatureCollection", "features": []}).encode(), ex=86400 * 7),
        call(centroid_cache_key, json.dumps({"type": "FeatureCollection", "features": []}).encode(), ex=86400 * 7),
    ]

    mocked_redis_set.assert_has_calls(set_calls)  # Wrongly caching the responses

    ### redis_client.delete calls ###
    mocked_redis_delete.assert_has_calls(
        [call(address_cache_key), call(centroid_cache_key)]
    )  #  Ensure we don’t serve the wrongly empty responses for others users

    ### Ensure we don’t break anything from the BAN API connector ###
    assert (
        mocked_search.call_count == 2
    )  # Searching the address, BAN API return wrongly an empty response, then falling back on asking for the centroid
    mocked_search.assert_any_call(
        {"q": "3 Rue de Valois", "postcode": "75001", "citycode": None, "city": "Paris", "autocomplete": 0, "limit": 1}
    )
    mocked_search.assert_any_call(
        {"q": "Paris", "postcode": "75001", "citycode": None, "type": "municipality", "autocomplete": 0, "limit": 1}
    )  # Connector fallback on the centroid because the `get_single_address_result` returned (falsy) empty
