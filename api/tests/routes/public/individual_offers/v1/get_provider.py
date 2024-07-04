import pytest

from pcapi.core.offerers import factories as offerers_factories

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


class GetProviderTest:
    PROVIDER_URL = "/public/providers/v1/provider"

    def test_return_provider_information_with_charlie(self, client):
        provider, _ = utils.create_offerer_provider(with_charlie=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(self.PROVIDER_URL)

        assert response.status_code == 200
        assert response.json == {
            "id": provider.id,
            "name": provider.name,
            "logoUrl": provider.logoUrl,
            "notificationUrl": None,
            "bookingUrl": provider.bookingExternalUrl,
            "cancelUrl": provider.cancelExternalUrl,
        }

    def test_raiser_401(self, client):
        response = client.get(self.PROVIDER_URL)
        assert response.status_code == 401
