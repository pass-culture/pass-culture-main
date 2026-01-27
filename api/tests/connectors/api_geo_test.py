import pytest

from pcapi.connectors import api_geo


@pytest.mark.settings(GEO_API_BACKEND="pcapi.connectors.api_geo.GeoApiBackend")
def test_search_city_by_name(requests_mock):
    requests_mock.get(
        "https://geo.api.gouv.fr/communes?boost=population&limit=20&nom=Chamon",
        json=[
            {
                "nom": "Saint-Chamond",
                "code": "42207",
                "codeDepartement": "42",
                "siren": "214202079",
                "codeEpci": "244200770",
                "codeRegion": "84",
                "codesPostaux": ["42400"],
                "population": 35586,
                "_score": 0.7547919309891216,
            },
            {
                "nom": "Chamonix-Mont-Blanc",
                "code": "74056",
                "codeDepartement": "74",
                "siren": "217400563",
                "codeEpci": "200023372",
                "codeRegion": "84",
                "codesPostaux": ["74400"],
                "population": 8673,
                "_score": 0.44845512493315143,
            },
            {
                "nom": "L'Hôme-Chamondot",
                "code": "61206",
                "codeDepartement": "61",
                "siren": "216102061",
                "codeEpci": "200068856",
                "codeRegion": "28",
                "codesPostaux": ["61290"],
                "population": 260,
                "_score": 0.40930973601906906,
            },
        ],
    )
    results = api_geo.search_city("Chamon")
    assert requests_mock.called
    assert results == [
        api_geo.GeoCity(insee_code="42207", name="Saint-Chamond"),
        api_geo.GeoCity(insee_code="74056", name="Chamonix-Mont-Blanc"),
        api_geo.GeoCity(insee_code="61206", name="L'Hôme-Chamondot"),
    ]


@pytest.mark.settings(GEO_API_BACKEND="pcapi.connectors.api_geo.GeoApiBackend")
def test_search_city_empty_query(requests_mock):
    requests_mock.get(
        "https://geo.api.gouv.fr/communes?boost=population&limit=20&nom=",
        json=[],
    )
    results = api_geo.search_city("")
    assert not requests_mock.called
    assert results == []


@pytest.mark.settings(GEO_API_BACKEND="pcapi.connectors.api_geo.GeoApiBackend")
def test_search_city_no_result(requests_mock):
    requests_mock.get(
        "https://geo.api.gouv.fr/communes?boost=population&limit=20&nom=n%27importe+quoi",
        json=[],
    )
    results = api_geo.search_city("n'importe quoi")
    assert requests_mock.called
    assert results == []


@pytest.mark.settings(GEO_API_BACKEND="pcapi.connectors.api_geo.GeoApiBackend")
def test_search_city_by_code(requests_mock):
    requests_mock.get(
        "https://geo.api.gouv.fr/communes?boost=population&limit=20&code=73047",
        json=[
            {
                "nom": "Bonneval-sur-Arc",
                "code": "73047",
                "codeDepartement": "73",
                "siren": "217300474",
                "codeEpci": "200070340",
                "codeRegion": "84",
                "codesPostaux": ["73480"],
                "population": 270,
            }
        ],
    )
    results = api_geo.search_city(insee_code="73047")
    assert requests_mock.called
    assert results == [
        api_geo.GeoCity(insee_code="73047", name="Bonneval-sur-Arc"),
    ]


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (400, api_geo.InvalidFormatException),
        (429, api_geo.RateLimitExceeded),
        (500, api_geo.GeoApiException),
        (503, api_geo.GeoApiException),
    ],
)
@pytest.mark.settings(GEO_API_BACKEND="pcapi.connectors.api_geo.GeoApiBackend")
def test_error_handling(status_code, expected_exception, requests_mock):
    requests_mock.get("https://geo.api.gouv.fr/communes", status_code=status_code)

    with pytest.raises(expected_exception):
        api_geo.search_city("exception")
