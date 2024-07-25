import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers import api as providers_api
from pcapi.core.providers import repository as providers_repository
import pcapi.core.providers.factories as providers_factories


@pytest.mark.usefixtures("db_session")
def test_delete_venue_provider(client):
    # Given
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    provider = providers_factories.PublicApiProviderFactory()
    venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)

    # VenueProvider sub tables
    providers_repository.add_all_permissions_for_venue_provider(venue_provider=venue_provider)
    providers_api.update_venue_provider_external_urls(venue_provider, notification_external_url="https://notify.com")

    # When
    response = client.with_session_auth(email=user_offerer.user.email).delete(f"/venueProviders/{venue_provider.id}")

    # Then
    assert response.status_code == 204


@pytest.mark.usefixtures("db_session")
def test_delete_venue_provider_should_return_404(client):
    # Given
    user_offerer = offerers_factories.UserOffererFactory()
    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # When
    response = client.with_session_auth(email=user_offerer.user.email).delete("/venueProviders/12345")

    # Then
    assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
def test_delete_venue_provider_should_return_403(client):
    # Given
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory()
    provider = providers_factories.PublicApiProviderFactory()
    venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)

    # When
    response = client.with_session_auth(email=user_offerer.user.email).delete(f"/venueProviders/{venue_provider.id}")

    # Then
    assert response.status_code == 403
