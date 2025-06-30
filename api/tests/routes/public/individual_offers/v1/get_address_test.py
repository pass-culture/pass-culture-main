import pytest

from pcapi.core.geography import factories as geography_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class GetAddressTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/addresses/{address_id}"
    endpoint_method = "get"
    default_path_params = {"address_id": 1}

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select address

    def test_should_return_address(self):
        plain_api_key, _ = self.setup_provider()
        geography_factories.AddressFactory(banId="un_Autre_ban_id", inseeCode=None)
        address = geography_factories.AddressFactory(
            banId="75101_8635_00182",
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )
        address_id = address.id

        result = self.make_request(plain_api_key=plain_api_key, path_params={"address_id": address_id})
        assert result.status_code == 200
        assert result.json == {
            "id": address_id,
            "banId": "75101_8635_00182",
            "postalCode": "75001",
            "city": "Paris",
            "street": "182 Rue Saint-Honoré",
            "latitude": 48.86696,
            "longitude": 2.31014,
        }

    def test_should_raise_404_because_address_not_found(self):
        plain_api_key, _ = self.setup_provider()
        address = geography_factories.AddressFactory(
            banId="75101_8635_00182",
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )
        not_existing_id = address.id + 1

        result = self.make_request(plain_api_key=plain_api_key, path_params={"address_id": not_existing_id})
        assert result.status_code == 404
        assert result.json == {"address": "We could not find any address for the given `id`"}
