from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


class GetProviderTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/providers/v1/provider"
    endpoint_method = "get"

    def test_should_raise_401_because_api_key_is_not_linked_to_provider(self):
        old_api_key = self.setup_old_api_key()
        response = self.make_request(old_api_key)
        assert response.status_code == 401
        assert response.json == {"auth": "Deprecated API key. Please contact provider support to get a new API key"}

    def test_return_provider_information(self):
        plain_api_key, provider = self.setup_provider()

        response = self.make_request(plain_api_key)

        assert response.status_code == 200
        assert response.json == {
            "id": provider.id,
            "name": provider.name,
            "logoUrl": provider.logoUrl,
            "notificationUrl": provider.notificationExternalUrl,
            "bookingUrl": provider.bookingExternalUrl,
            "cancelUrl": provider.cancelExternalUrl,
        }
