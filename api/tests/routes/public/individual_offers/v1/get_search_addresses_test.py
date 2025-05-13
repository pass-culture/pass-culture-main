from unittest.mock import patch

import pytest

from pcapi.connectors.api_adresse import AddressInfo
from pcapi.connectors.api_adresse import NoResultException
from pcapi.core.geography import factories as geography_factories

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class SearchAddressesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/addresses/search"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select address

    @staticmethod
    def _get_base_query() -> dict:
        return {
            "postalCode": "75001",
            "city": "Paris",
            "street": "182 rue St Honoré",
            "latitude": 48.86696,
            "longitude": 2.31014,
        }

    def set_base_resources(self):
        # French Ministry of Culture
        ban_address = geography_factories.AddressFactory(
            banId="75101_8635_00182",
            postalCode="75101",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )
        manual_address = geography_factories.ManualAddressFactory(
            postalCode="71640",
            city="Saint-Jean-de-Vaux",
            street="Dans le champ derrière chez oim",
            latitude=46.81201,
            longitude=4.70024,
        )
        return ban_address, manual_address

    @pytest.mark.parametrize(
        "partial_query,expected_json",
        [
            (
                {"postalCode": "7500"},
                {"postalCode": ['string does not match regex "^(?:0[1-9]|[1-8]\\d|9[0-8])\\d{3}$"']},
            ),
            ({"city": "a" * 201}, {"city": ["ensure this value has at most 200 characters"]}),
            ({"street": "a" * 201}, {"street": ["ensure this value has at most 200 characters"]}),
            ({"city": ""}, {"city": ["ensure this value has at least 1 characters"]}),
            ({"street": ""}, {"street": ["ensure this value has at least 1 characters"]}),
            ({"latitude": 91}, {"latitude": ["ensure this value is less than or equal to 90"]}),
            ({"longitude": -183}, {"longitude": ["ensure this value is greater than or equal to -180"]}),
            ({"latitude": -92}, {"latitude": ["ensure this value is greater than or equal to -90"]}),
            ({"longitude": 190}, {"longitude": ["ensure this value is less than or equal to 180"]}),
            ({"latitude": "coucou"}, {"latitude": ["value is not a valid float"]}),
            ({"longitude": "hey"}, {"longitude": ["value is not a valid float"]}),
        ],
    )
    def test_should_raise_400_because_of_bad_params(self, client: TestClient, partial_query, expected_json):
        plain_api_key, _ = self.setup_provider()
        query = dict(self._get_base_query(), **partial_query)
        result = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params=query)

        assert result.status_code == 400
        assert result.json == expected_json

    @pytest.mark.parametrize(
        "missing_param,expected_json",
        [
            ("postalCode", {"postalCode": ["field required"]}),
            ("city", {"city": ["field required"]}),
            ("street", {"street": ["field required"]}),
            ("latitude", {"__root__": ["`latitude` must be set if `longitude` is provided"]}),
            ("longitude", {"__root__": ["`longitude` must be set if `latitude` is provided"]}),
        ],
    )
    def test_should_raise_400_because_of_missing_params(self, client: TestClient, missing_param, expected_json):
        plain_api_key, _ = self.setup_provider()
        query = self._get_base_query()
        query.pop(missing_param)
        result = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params=query)

        assert result.status_code == 400
        assert result.json == expected_json

    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_return_existing_address_based_on_address_returned_by_the_ban_api(
        self, get_address_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()
        exiting_address, _ = self.set_base_resources()
        get_address_mock.return_value = AddressInfo(
            id="75101_8635_00182",
            postcode="75101",
            citycode="8635",  # inseeCode
            latitude=48.86696,
            longitude=2.31014,
            score=0.98,
            city="Paris",
            street="182 Rue Saint-Honoré",
        )
        result = client.with_explicit_token(plain_api_key).get(self.endpoint_url, params=self._get_base_query())

        get_address_mock.assert_called_once_with(
            address="182 rue St Honoré", postcode="75001", city="Paris", strict=True
        )
        assert result.status_code == 200
        assert result.json == {
            "addresses": [
                {
                    "id": exiting_address.id,
                    "banId": "75101_8635_00182",
                    "postalCode": "75101",
                    "city": "Paris",
                    "street": "182 Rue Saint-Honoré",
                    "latitude": 48.86696,
                    "longitude": 2.31014,
                }
            ]
        }

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_return_existing_address_based_on_municipality(
        self, get_address_mock, get_municipality_centroid_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()
        _, manual_address = self.set_base_resources()

        get_address_mock.side_effect = NoResultException()  # mock no result from BAN API
        get_municipality_centroid_mock.return_value = AddressInfo(
            id="71430",
            postcode="71640",
            citycode="71430",  # inseeCode
            latitude=46.808463,
            longitude=4.701174,
            score=0.93,
            city="Saint-Jean-de-Vaux",
            street="unused",
        )

        result = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url,
            params={"postalCode": "71640", "city": "St Jean de Vaux", "street": "Dans le champ derrière chez oim"},
        )

        get_address_mock.assert_called_once_with(
            address="Dans le champ derrière chez oim", postcode="71640", city="St Jean de Vaux", strict=True
        )
        get_municipality_centroid_mock.assert_called_once_with(postcode="71640", city="St Jean de Vaux")
        assert result.status_code == 200
        assert result.json == {
            "addresses": [
                {
                    "id": manual_address.id,
                    "banId": None,
                    "postalCode": "71640",
                    "city": "Saint-Jean-de-Vaux",
                    "street": "Dans le champ derrière chez oim",
                    "latitude": 46.81201,
                    "longitude": 4.70024,
                }
            ]
        }

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_return_existing_address_based_on_municipality_and_client_postal_code(
        self, get_address_mock, get_municipality_centroid_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()

        manual_address = geography_factories.ManualAddressFactory(
            postalCode="75016",
            city="Paris",
            street="Carrefour des Tribunes",
            latitude=46.81201,
            longitude=4.70024,
        )

        get_address_mock.side_effect = NoResultException()  # mock no result from BAN API
        get_municipality_centroid_mock.return_value = AddressInfo(
            id="75056",
            postcode="75001",  # incorrect postal code
            citycode="75056",
            latitude=48.859,
            longitude=2.347,
            score=0.667307878787879,
            city="Paris",
            street="unused",
        )

        result = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url,
            params={"postalCode": "75016", "city": "Paris", "street": "Carrefour des Tribunes"},
        )

        assert result.status_code == 200
        assert result.json == {
            "addresses": [
                {
                    "id": manual_address.id,
                    "banId": None,
                    "postalCode": "75016",
                    "city": "Paris",
                    "street": "Carrefour des Tribunes",
                    "latitude": 46.81201,
                    "longitude": 4.70024,
                }
            ]
        }

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_raise_400_because_municipality_not_found_on_BAN_API(
        self, get_address_mock, get_municipality_centroid_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()
        self.set_base_resources()
        # mock no result from BAN API
        get_address_mock.side_effect = NoResultException()
        get_municipality_centroid_mock.side_effect = NoResultException()

        result = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url,
            params={
                "postalCode": "75017",
                "city": "Parisse (comme disent les Anglais)",
                "street": "Place Perave de ouf",
            },
        )

        get_address_mock.assert_called_once_with(
            address="Place Perave de ouf", postcode="75017", city="Parisse (comme disent les Anglais)", strict=True
        )
        get_municipality_centroid_mock.assert_called_once_with(
            postcode="75017", city="Parisse (comme disent les Anglais)"
        )

        assert result.status_code == 400
        assert result.json == {
            "__root__": ["No municipality found for `city=Parisse (comme disent les Anglais)` and `postalCode=75017`"]
        }
