import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers import api as providers_api


@pytest.mark.usefixtures("db_session")
def test_delete_venue_provider(client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    provider = providers_factories.PublicApiProviderFactory()
    venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)

    providers_api.update_venue_provider_external_urls(venue_provider, notification_external_url="https://notify.com")

    response = client.with_session_auth(email=user_offerer.user.email).delete(f"/venue-providers/{venue_provider.id}")

    assert response.status_code == 204


@pytest.mark.usefixtures("db_session")
def test_delete_venue_provider_should_return_404(client):
    user_offerer = offerers_factories.UserOffererFactory()
    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    response = client.with_session_auth(email=user_offerer.user.email).delete("/venue-providers/12345")

    assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
def test_delete_venue_provider_should_return_403(client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory()
    provider = providers_factories.PublicApiProviderFactory()
    venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)

    response = client.with_session_auth(email=user_offerer.user.email).delete(f"/venue-providers/{venue_provider.id}")

    assert response.status_code == 403
