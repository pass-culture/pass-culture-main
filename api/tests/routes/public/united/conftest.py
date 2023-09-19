import pytest

from pcapi.core.educational import factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories


@pytest.fixture(name="api_key")
def api_key_fixture():
    provider = providers_factories.ProviderFactory()
    return offerers_factories.ApiKeyFactory(provider=provider)


@pytest.fixture(name="api_client")
def api_client_fixture(client, api_key):
    return client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)


@pytest.fixture(name="venue")
def venue_fixture(api_key):
    return providers_factories.VenueProviderFactory(provider=api_key.provider).venue


@pytest.fixture(name="unrelated_venue")
def unrelated_venue_fixture():
    provider = providers_factories.ProviderFactory()
    return providers_factories.VenueProviderFactory(provider=provider).venue


@pytest.fixture(name="offerer")
def offerer_fixture(venue):
    return venue.managingOfferer


@pytest.fixture(name="related_offerer")
def related_offerer_fixture(api_key):
    # offerer and related_offerer are linked to the same provider
    # this should be useful to test some filtering actions.
    vp = providers_factories.VenueProviderFactory(provider=api_key.provider)
    return vp.venue.managingOfferer


@pytest.fixture(name="collective_offer")
def collective_venue_fixture(venue):
    return educational_factories.CollectiveOfferFactory(venue=venue)


@pytest.fixture(name="collective_stock")
def collective_stock_fixture(collective_offer):
    return educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)


@pytest.fixture(name="collective_booking")
def collective_booking_fixture(collective_stock):
    return educational_factories.CollectiveBookingFactory(collectiveStock=collective_stock)
