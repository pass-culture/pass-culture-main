from unittest.mock import patch

import pytest

from pcapi.core.geography import factories as geography_factories
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.testing import override_settings

from tests.conftest import TestClient
from tests.connectors.api_adresse import fixtures
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class PostAddressTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/addresses"
    endpoint_method = "post"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select address

    @staticmethod
    def _get_base_payload() -> dict:
        return {
            "postalCode": "75001",
            "city": "Paris",
            "street": "182 Rue Saint-Honoré",
            "latitude": 48.86696,
            "longitude": 2.31014,
        }

    @pytest.mark.parametrize(
        "partial_payload,expected_json",
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
    def test_should_raise_400_because_of_bad_params(self, client: TestClient, partial_payload, expected_json):
        plain_api_key, _ = self.setup_provider()
        request_payload = dict(self._get_base_payload(), **partial_payload)
        result = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=request_payload)

        assert result.status_code == 400
        assert result.json == expected_json

    def test_should_raise_400_because_address_already_existst(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        geography_factories.AddressFactory(
            banId="75101_8635_00182",
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )

        result = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=self._get_base_payload())

        assert result.status_code == 400
        assert result.json == {"global": "address already exists"}

    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    def test_should_set_is_manual_edition_to_true_if_address_not_found_on_ban_api(
        self, client: TestClient, requests_mock
    ):
        plain_api_key, _ = self.setup_provider()
        requests_mock.get("https://api-adresse.data.gouv.fr/search", json=fixtures.NO_FEATURE_RESPONSE)
        payload = self._get_base_payload()

        with patch(
            "pcapi.core.offerers.api.create_offerer_address_from_address_api"
        ) as create_offerer_address_from_address_api_mock:
            create_offerer_address_from_address_api_mock.return_value = geography_models.Address(
                banId=None,
                inseeCode=None,
                postalCode="75001",
                city="Paris",
                street="182 Rue Saint-Honoré",
                latitude=48.86696,
                longitude=2.31014,
            )
            result = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=self._get_base_payload())

        create_offerer_address_from_address_api_mock.assert_called_once_with(
            offerers_schemas.AddressBodyModel(
                street=payload["street"],
                postalCode=payload["postalCode"],
                latitude=payload["latitude"],
                longitude=payload["longitude"],
                city=payload["city"],
                isManualEdition=True,  # what we want to check
            )
        )
        assert result.status_code == 200
        assert result.json == {
            "banId": None,
            "postalCode": "75001",
            "city": "Paris",
            "street": "182 Rue Saint-Honoré",
            "latitude": 48.86696,
            "longitude": 2.31014,
        }

    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    def test_should_set_is_manual_edition_to_false_if_address_is_found_on_ban_api(
        self, client: TestClient, requests_mock
    ):
        plain_api_key, _ = self.setup_provider()
        requests_mock.get("https://api-adresse.data.gouv.fr/search", json=fixtures.ONE_FEATURE_RESPONSE)
        payload = self._get_base_payload()

        with patch(
            "pcapi.core.offerers.api.create_offerer_address_from_address_api"
        ) as create_offerer_address_from_address_api_mock:
            create_offerer_address_from_address_api_mock.return_value = geography_models.Address(
                banId="75101_8635_00182",
                inseeCode=None,
                postalCode="75001",
                city="Paris",
                street="182 Rue Saint-Honoré",
                latitude=48.86696,
                longitude=2.31014,
            )
            result = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=self._get_base_payload())

        create_offerer_address_from_address_api_mock.assert_called_once_with(
            offerers_schemas.AddressBodyModel(
                street=payload["street"],
                postalCode=payload["postalCode"],
                latitude=payload["latitude"],
                longitude=payload["longitude"],
                city=payload["city"],
                isManualEdition=False,  # what we want to check
            )
        )
        assert result.status_code == 200
        assert result.json == {
            "banId": "75101_8635_00182",
            "postalCode": "75001",
            "city": "Paris",
            "street": "182 Rue Saint-Honoré",
            "latitude": 48.86696,
            "longitude": 2.31014,
        }
