import pytest

from pcapi.core.providers import models as providers_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class E2EOfferTest:
    endpoint_url = "/e2e/provider"

    def _base_payload(self):
        return {
            "name": "E2E provider",
            "bookingExternalUrl": "http://bookingExternalUrl.test",
            "cancelExternalUrl": "http://cancelExternalUrl.test",
            "notificationExternalUrl": "http://notificationExternalUrl.test",
        }

    def test_unauthorized(self, client):
        response = client.post(self.endpoint_url, self._base_payload())
        assert response.status_code == 401

    def test_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        response = client.post(self.endpoint_url, json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 401

    def test_create_provider(self, auth_client):
        response = auth_client.post(self.endpoint_url, self._base_payload())
        assert response.status_code == 200

        providers = (
            db.session.query(providers_models.Provider).filter(providers_models.Provider.name == "E2E provider").all()
        )

        assert len(providers) == 1
        provider = providers[0]
        assert provider.name == "E2E provider"
        assert provider.bookingExternalUrl == "http://bookingExternalUrl.test"
        assert provider.cancelExternalUrl == "http://cancelExternalUrl.test"
        assert provider.notificationExternalUrl == "http://notificationExternalUrl.test"

        assert response.json["id"] == provider.id
        assert response.json["name"] == "E2E provider"
        assert response.json["bookingExternalUrl"] == "http://bookingExternalUrl.test"
        assert response.json["cancelExternalUrl"] == "http://cancelExternalUrl.test"
        assert response.json["notificationExternalUrl"] == "http://notificationExternalUrl.test"

    def test_create_provider_with_empty_url(self, auth_client):
        response = auth_client.post(self.endpoint_url, self._base_payload())
        assert response.status_code == 200

        providers = (
            db.session.query(providers_models.Provider).filter(providers_models.Provider.name == "E2E provider").all()
        )

        assert len(providers) == 1
        provider = providers[0]
        assert provider.name == "E2E provider"
        assert provider.bookingExternalUrl == "http://bookingExternalUrl.test"
        assert provider.cancelExternalUrl == "http://cancelExternalUrl.test"
        assert provider.notificationExternalUrl == "http://notificationExternalUrl.test"

        assert response.json["id"] == provider.id
        assert response.json["name"] == "E2E provider"
        assert response.json["bookingExternalUrl"] == "http://bookingExternalUrl.test"
        assert response.json["cancelExternalUrl"] == "http://cancelExternalUrl.test"
        assert response.json["notificationExternalUrl"] == "http://notificationExternalUrl.test"
