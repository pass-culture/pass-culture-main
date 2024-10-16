from unittest.mock import patch

import pytest

from pcapi.connectors.api_adresse import AddressInfo
from pcapi.connectors.api_adresse import NoResultException
from pcapi.core.geography import factories as geography_factories
from pcapi.core.geography import models as geography_models

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CreateAddressTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/addresses"
    endpoint_method = "post"

    @staticmethod
    def _get_base_body() -> dict:
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
        manual_address = geography_factories.AddressFactory(
            banId=None,
            inseeCode=None,
            postalCode="71640",
            city="Saint-Jean-de-Vaux",
            street="Dans le champ derrière chez oim",
            latitude=46.81201,
            longitude=4.70024,
            isManualEdition=True,
        )
        return ban_address, manual_address

    @pytest.mark.parametrize(
        "partial_body,expected_json",
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
    def test_should_raise_400_because_of_bad_params(self, client: TestClient, partial_body, expected_json):
        plain_api_key, _ = self.setup_provider()
        body = dict(self._get_base_body(), **partial_body)
        result = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=body)

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
        body = self._get_base_body()
        body.pop(missing_param)
        result = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=body)

        assert result.status_code == 400
        assert result.json == expected_json

    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_add_an_address_using_the_ban_api(self, get_address_mock, client: TestClient):
        plain_api_key, _ = self.setup_provider()

        get_address_mock.return_value = AddressInfo(
            id="75101_8635_00182",
            postcode="75101",
            citycode="75108",  # inseeCode
            latitude=48.86696,
            longitude=2.31014,
            score=0.98,
            city="Paris",
            street="182 Rue Saint-Honoré",
        )
        result = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=self._get_base_body())

        get_address_mock.assert_called_once_with(
            address="182 rue St Honoré", postcode="75001", city="Paris", strict=True
        )
        created_address = geography_models.Address.query.filter(
            geography_models.Address.banId == "75101_8635_00182"
        ).one_or_none()

        assert created_address is not None
        assert not created_address.isManualEdition
        assert result.status_code == 200
        assert result.json == {
            "id": created_address.id,
            "banId": "75101_8635_00182",
            "postalCode": "75101",
            "city": "Paris",
            "street": "182 Rue Saint-Honoré",
            "latitude": 48.86696,
            "longitude": 2.31014,
        }

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_return_add_an_address_using_the_municipality(
        self, get_address_mock, get_municipality_centroid_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()

        get_address_mock.side_effect = NoResultException()  # mock no result from BAN API
        get_municipality_centroid_mock.return_value = AddressInfo(
            id="71430",
            postcode="71640",
            citycode="71430",
            latitude=46.808463,
            longitude=4.701174,
            score=0.93,
            city="Saint-Jean-de-Vaux",
            street=None,
        )

        result = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "postalCode": "71640",
                "city": "St Jean de Vaux",
                "street": "Dans le champ derrière chez oim",
                "latitude": 46.80847,
                "longitude": 4.70118,
            },
        )

        get_address_mock.assert_called_once_with(
            address="Dans le champ derrière chez oim", postcode="71640", city="St Jean de Vaux", strict=True
        )
        get_municipality_centroid_mock.assert_called_once_with(postcode="71640", city="St Jean de Vaux")
        created_address = geography_models.Address.query.filter(
            geography_models.Address.inseeCode == "71430"
        ).one_or_none()

        assert created_address is not None
        assert created_address.isManualEdition
        assert result.status_code == 200
        assert result.json == {
            "id": created_address.id,
            "banId": None,
            "postalCode": "71640",
            "city": "Saint-Jean-de-Vaux",
            "street": "Dans le champ derrière chez oim",
            "latitude": 46.80847,
            "longitude": 4.70118,
        }

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_raise_400_because_municipality_not_found_on_BAN_API(
        self, get_address_mock, get_municipality_centroid_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()
        # mock no result from BAN API
        get_address_mock.side_effect = NoResultException()
        get_municipality_centroid_mock.side_effect = NoResultException()

        result = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "postalCode": "75017",
                "city": "Parisse (comme disent les Anglais)",
                "street": "Place Perave de ouf",
                "latitude": 48.86696,
                "longitude": 2.31014,
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
            "__root__": [f"No municipality found for `city=Parisse (comme disent les Anglais)` and `postalCode=75017`"]
        }

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_raise_400_because_specific_address_not_found_on_BAN_API_and_lat_long_not_given(
        self, get_address_mock, get_municipality_centroid_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()

        get_address_mock.side_effect = NoResultException()  # mock no result from BAN API
        get_municipality_centroid_mock.return_value = AddressInfo(
            id="71430",
            postcode="71640",
            citycode="71430",
            latitude=46.808463,
            longitude=4.701174,
            score=0.93,
            city="Saint-Jean-de-Vaux",
            street=None,
        )

        result = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "postalCode": "71640",
                "city": "St Jean de Vaux",
                "street": "Dans le champ derrière chez oim",
            },
        )

        get_address_mock.assert_called_once_with(
            address="Dans le champ derrière chez oim", postcode="71640", city="St Jean de Vaux", strict=True
        )
        get_municipality_centroid_mock.assert_called_once_with(postcode="71640", city="St Jean de Vaux")

        assert result.status_code == 400
        assert result.json == {
            "__root__": [
                "The address you provided could not be found in the BAN API. Please provide valid `latitude` and `longitude` coordinates for this address to proceed."
            ]
        }
