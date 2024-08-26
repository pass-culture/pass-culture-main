from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


class GetProviderTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/providers/v1/provider"
    endpoint_method = "get"

    def test_should_raise_401_because_api_key_is_not_linked_to_provider(self, client: TestClient):
        old_api_key = self.setup_old_api_key()
        response = client.with_explicit_token(old_api_key).get(self.endpoint_url)
        assert response.status_code == 401
        assert response.json == {"auth": "Deprecated API key. Please contact provider support to get a new API key"}

    def test_return_provider_information(self, client):
        plain_api_key, provider = self.setup_provider()

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)

        assert response.status_code == 200
        assert response.json == {
            "id": provider.id,
            "name": provider.name,
            "logoUrl": provider.logoUrl,
            "notificationUrl": provider.notificationExternalUrl,
            "bookingUrl": provider.bookingExternalUrl,
            "cancelUrl": provider.cancelExternalUrl,
        }
