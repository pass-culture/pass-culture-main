import pytest

from pcapi.core.geography import factories as geography_factories

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class GetAddressTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/addresses"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select address

    @pytest.mark.parametrize(
        "query_params,expected_json",
        [
            (
                {},
                {"__root__": ["Either `latitude/longitude` or `banId` must be set"]},
            ),
            (
                {"latitude": 48.8669567, "longitude": 2.310144, "banId": "some_id"},
                {
                    "__root__": [
                        "`latitude/longitude` and `banId` cannot be both set. Use either `latitude/longitude` or `banId`"
                    ]
                },
            ),
            ({"latitude": 48.8669567}, {"__root__": ["`longitude` must be set if `latitude` is provided"]}),
            ({"longitude": 2.310144}, {"__root__": ["`latitude` must be set if `longitude` is provided"]}),
            (
                {"latitude": 91, "longitude": -183},
                {
                    "latitude": ["ensure this value is less than or equal to 90"],
                    "longitude": ["ensure this value is greater than or equal to -180"],
                },
            ),
            (
                {"latitude": -92, "longitude": 190},
                {
                    "latitude": ["ensure this value is greater than or equal to -90"],
                    "longitude": ["ensure this value is less than or equal to 180"],
                },
            ),
            (
                {"latitude": "coucou", "longitude": "hey"},
                {
                    "latitude": ["value is not a valid float"],
                    "longitude": ["value is not a valid float"],
                },
            ),
        ],
    )
    def test_should_raise_400_because_of_bad_params(self, client: TestClient, query_params, expected_json):
        plain_api_key, _ = self.setup_provider()
        result = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params=query_params)

        assert result.status_code == 400
        assert result.json == expected_json

    @pytest.mark.parametrize(
        "query_params",
        [
            {"banId": "75101_8635_00182"},
            {"latitude": 48.8669567, "longitude": 2.3101443},
            {"latitude": 48.86696, "longitude": 2.31014},  # five decimal places
        ],
    )
    def test_should_return_address(self, client: TestClient, query_params):
        plain_api_key, _ = self.setup_provider()
        geography_factories.AddressFactory(banId="un_Autre_ban_id", inseeCode=None)
        geography_factories.AddressFactory(
            banId="75101_8635_00182",
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )

        result = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params=query_params)
        assert result.status_code == 200
        assert result.json == {
            "banId": "75101_8635_00182",
            "postalCode": "75001",
            "city": "Paris",
            "street": "182 Rue Saint-Honoré",
            "latitude": 48.86696,
            "longitude": 2.31014,
        }

    @pytest.mark.parametrize(
        "query_params, expected_json",
        [
            ({"banId": "coucou"}, {"address": "We could not find any address for the given `banId`"}),
            (
                {"latitude": 47.903, "longitude": 2.3101443},
                {"address": "We could not find any address for the given `latitude/longitude`"},
            ),
        ],
    )
    def test_should_raise_404_because_address_not_found(self, client: TestClient, query_params, expected_json):
        plain_api_key, _ = self.setup_provider()
        geography_factories.AddressFactory(banId="un_Autre_ban_id", inseeCode=None)
        geography_factories.AddressFactory(
            banId="75101_8635_00182",
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )

        result = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params=query_params)
        assert result.status_code == 404
        assert result.json == expected_json
