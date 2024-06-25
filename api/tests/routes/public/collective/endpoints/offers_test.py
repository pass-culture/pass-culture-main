from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="public_client")
def public_client_fixture(client):
    return client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)


class GetCollectiveFormatsTest:
    endpoint = "public_api.get_offers_formats"

    def test_get_formats(self, public_client):
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        response = public_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert sorted(
            [{"name": fmt.value, "id": fmt.name} for fmt in subcategories.EacFormat], key=lambda x: x["id"]
        ) == sorted(response.json, key=lambda x: x["id"])
