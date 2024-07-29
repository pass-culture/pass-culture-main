from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


class GetProviderTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/providers/v1/provider"

    def test_should_raise_401_because_not_authenticated(self, client):
        response = client.get(self.endpoint_url)
        assert response.status_code == 401

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
