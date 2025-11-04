import pytest

from pcapi.core.providers import factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_isFromAllocineProvider():
    allocine = factories.AllocineProviderFactory()
    allocine_venue_provider = factories.VenueProviderFactory(provider=allocine)
    assert allocine_venue_provider.isFromAllocineProvider

    other = factories.ProviderFactory(localClass="Dummy")
    other_venue_provider = factories.VenueProviderFactory(provider=other)
    assert not other_venue_provider.isFromAllocineProvider
