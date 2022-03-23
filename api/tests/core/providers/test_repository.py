import pytest

from pcapi.core.providers import factories
from pcapi.core.providers import repository


@pytest.mark.usefixtures("db_session")
def test_get_venue_provider_by_id_regular_venue_provider():
    provider = factories.VenueProviderFactory()
    assert repository.get_venue_provider_by_id(provider.id) == provider


@pytest.mark.usefixtures("db_session")
def test_get_venue_provider_by_id_allocine_venue_provider():
    provider = factories.AllocineVenueProviderFactory()
    assert repository.get_venue_provider_by_id(provider.id) == provider


@pytest.mark.usefixtures("db_session")
def test_get_active_venue_providers_by_provider():
    provider = factories.ProviderFactory()
    vp1 = factories.VenueProviderFactory(provider=provider, isActive=True)
    factories.VenueProviderFactory(provider=provider, isActive=False)
    factories.VenueProviderFactory()

    assert repository.get_active_venue_providers_by_provider(provider.id) == [vp1]
