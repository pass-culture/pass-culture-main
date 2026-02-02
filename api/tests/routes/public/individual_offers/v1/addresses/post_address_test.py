from unittest.mock import patch

import pytest

from pcapi.connectors.api_adresse import AddressInfo
from pcapi.connectors.api_adresse import AdresseApiServerErrorException
from pcapi.connectors.api_adresse import NoResultException
from pcapi.core.geography import factories as geography_factories
from pcapi.core.geography import models as geography_models
from pcapi.models import db

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CreateAddressTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/addresses"
    endpoint_method = "post"

    @staticmethod
    def _get_base_payload() -> dict:
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
        "payload,expected_json",
        [
            (
                {"postalCode": "7500"},
                {"postalCode": ["String should match pattern '^(?:0[1-9]|[1-8]\\d|9[0-8])\\d{3}$'"]},
            ),
            ({"city": "a" * 201}, {"city": ["String should have at most 200 characters"]}),
            ({"street": "a" * 201}, {"street": ["String should have at most 200 characters"]}),
            ({"city": ""}, {"city": ["String should have at least 1 character"]}),
            ({"street": ""}, {"street": ["String should have at least 1 character"]}),
            ({"latitude": 91}, {"latitude": ["Input should be less than or equal to 90"]}),
            ({"longitude": -183}, {"longitude": ["Input should be greater than or equal to -180"]}),
            ({"latitude": -92}, {"latitude": ["Input should be greater than or equal to -90"]}),
            ({"longitude": 190}, {"longitude": ["Input should be less than or equal to 180"]}),
            (
                {"latitude": "coucou"},
                {"latitude": ["Input should be a valid number, unable to parse string as a number"]},
            ),
            (
                {"longitude": "hey"},
                {"longitude": ["Input should be a valid number, unable to parse string as a number"]},
            ),
        ],
    )
    def test_should_raise_400_because_of_bad_params(self, payload, expected_json):
        plain_api_key, _ = self.setup_provider()
        payload = dict(self._get_base_payload(), **payload)

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 400
        assert response.json == expected_json

    @pytest.mark.parametrize(
        "missing_param,expected_json",
        [
            ("postalCode", {"postalCode": ["Field required"]}),
            ("city", {"city": ["Field required"]}),
            ("street", {"street": ["Field required"]}),
            ("latitude", {"latitude": ["`latitude` must be set if `longitude` is provided"]}),
            ("longitude", {"longitude": ["`longitude` must be set if `latitude` is provided"]}),
        ],
    )
    def test_should_raise_400_because_of_missing_params(self, missing_param, expected_json):
        plain_api_key, _ = self.setup_provider()
        payload = self._get_base_payload()
        payload.pop(missing_param)

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 400
        assert response.json == expected_json

    @pytest.mark.parametrize(
        "address_exception,municipality_centroid_exception",
        [
            (AdresseApiServerErrorException(), None),  # 1st call fails
            (NoResultException(), AdresseApiServerErrorException()),  # 2nd call fails
        ],
    )
    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_raise_500_because_ban_api_is_unavailable(
        self,
        get_address_mock,
        get_municipality_centroid_mock,
        address_exception,
        municipality_centroid_exception,
    ):
        plain_api_key, _ = self.setup_provider()

        get_address_mock.side_effect = address_exception
        get_municipality_centroid_mock.side_effect = municipality_centroid_exception

        response = self.make_request(plain_api_key, json_body=self._get_base_payload())

        assert response.status_code == 500
        assert response.json == {"global": ["BAN API is unavailable"]}

    @patch("pcapi.connectors.api_adresse.get_address")
    def test_should_add_an_address_using_the_ban_api(self, get_address_mock):
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
        response = self.make_request(plain_api_key, json_body=self._get_base_payload())

        get_address_mock.assert_called_once_with(
            address="182 rue St Honoré", postcode="75001", city="Paris", strict=True
        )
        created_address = (
            db.session.query(geography_models.Address)
            .filter(geography_models.Address.banId == "75101_8635_00182")
            .one_or_none()
        )

        assert created_address is not None
        assert not created_address.isManualEdition
        assert response.status_code == 200
        assert response.json == {
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
        self, get_address_mock, get_municipality_centroid_mock
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
            street="unused",
        )

        response = self.make_request(
            plain_api_key,
            json_body={
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
        created_address = (
            db.session.query(geography_models.Address)
            .filter(geography_models.Address.inseeCode == "71430")
            .one_or_none()
        )

        assert created_address is not None
        assert created_address.isManualEdition
        assert response.status_code == 200
        assert response.json == {
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
    def test_should_use_postal_code_sent_by_client_in_case_the_address_not_found_on_the_ban_api(
        self, get_address_mock, get_municipality_centroid_mock, client: TestClient
    ):
        plain_api_key, _ = self.setup_provider()

        get_address_mock.side_effect = NoResultException()  # mock no result from BAN API
        get_municipality_centroid_mock.return_value = AddressInfo(
            id="75056",
            postcode="75001",
            citycode="75056",
            latitude=48.859,
            longitude=2.347,
            score=0.667307878787879,
            city="Paris",
            street="unused",
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "postalCode": "75016",
                "city": "Paris",
                "street": "Carrefour des Tribunes",
                "latitude": 46.80847,
                "longitude": 4.70118,
            },
        )

        created_address = (
            db.session.query(geography_models.Address)
            .filter(geography_models.Address.inseeCode == "75056")
            .one_or_none()
        )

        assert created_address is not None
        assert created_address.isManualEdition
        assert response.status_code == 200
        assert response.json == {
            "id": created_address.id,
            "banId": None,
            "postalCode": "75016",  # not 75001
            "city": "Paris",
            "street": "Carrefour des Tribunes",
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

        response = self.make_request(
            plain_api_key,
            json_body={
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

        assert response.status_code == 400
        assert response.json == {
            "__root__": ["No municipality found for `city=Parisse (comme disent les Anglais)` and `postalCode=75017`"]
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
            street="unused",
        )

        response = self.make_request(
            plain_api_key,
            json_body={"postalCode": "71640", "city": "St Jean de Vaux", "street": "Dans le champ derrière chez oim"},
        )

        get_address_mock.assert_called_once_with(
            address="Dans le champ derrière chez oim", postcode="71640", city="St Jean de Vaux", strict=True
        )
        get_municipality_centroid_mock.assert_called_once_with(postcode="71640", city="St Jean de Vaux")

        assert response.status_code == 400
        assert response.json == {
            "__root__": [
                "The address you provided could not be found in the BAN API. Please provide valid `latitude` and `longitude` coordinates for this address to proceed."
            ]
        }
