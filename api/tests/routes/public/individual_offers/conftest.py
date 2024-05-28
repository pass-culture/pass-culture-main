import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories


SECRET = "secret"
OTHER_SECRET = "other-secret"


@pytest.fixture(name="provider")
def provider_fixture():
    return providers_factories.ProviderFactory(
        name="Technical provider",
        localClass=None,
        isActive=True,
        enabledForPro=True,
        bookingExternalUrl=None,
        cancelExternalUrl=None,
    )


@pytest.fixture(name="offerer")
def offerer_fixture():
    return offerers_factories.OffererFactory(name="Technical provider")


@pytest.fixture(name="offerer_provider")
def offerer_provider_fixture(offerer, provider):
    return providers_factories.OffererProviderFactory(
        offerer=offerer,
        provider=provider,
    )


@pytest.fixture(name="venue")
def venue_fixture(provider):
    return providers_factories.VenueProviderFactory(
        provider=provider, venueIdAtOfferProvider="Test", isActive=True
    ).venue


@pytest.fixture(name="api_key")
def api_key_fixture(offerer_provider):
    return offerers_factories.ApiKeyFactory(
        offerer=offerer_provider.offerer,
        provider=offerer_provider.provider,
        secret=SECRET,
        prefix=f"{offerers_factories.DEFAULT_PREFIX}{offerer_provider.offerer.id}",
    )


@pytest.fixture(name="token")
def token_fixture(api_key):
    return offerers_factories.build_clear_api_key(api_key.prefix, SECRET)


@pytest.fixture(name="auth_client")
def auth_client(token, client):
    return client.with_explicit_token(token)


@pytest.fixture(name="event")
def event_fixture(venue, api_key):
    return offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)


@pytest.fixture(name="stock")
def stock_fixture(event, price_category):
    return offers_factories.StockFactory(offer=event, priceCategory=price_category)


@pytest.fixture(name="price_category")
def price_category_fixture(event):
    return offers_factories.PriceCategoryFactory(offer=event)


@pytest.fixture(name="other_provider")
def other_provider_fixture():
    return providers_factories.ProviderFactory(
        name="Other technical provider",
        localClass=None,
        isActive=True,
        enabledForPro=True,
        bookingExternalUrl=None,
        cancelExternalUrl=None,
    )


@pytest.fixture(name="other_offerer")
def other_offerer_fixture():
    return offerers_factories.OffererFactory(name="Other technical provider")


@pytest.fixture(name="other_offerer_provider")
def other_offerer_provider_fixture(other_offerer, other_provider):
    return providers_factories.OffererProviderFactory(
        offerer=other_offerer,
        provider=other_provider,
    )


@pytest.fixture(name="other_venue")
def other_venue_fixture(other_provider):
    return providers_factories.VenueProviderFactory(
        provider=other_provider, venueIdAtOfferProvider="Other test", isActive=True
    ).venue


@pytest.fixture(name="other_api_key")
def other_api_key_fixture(other_offerer_provider):
    return offerers_factories.ApiKeyFactory(
        offerer=other_offerer_provider.offerer,
        provider=other_offerer_provider.provider,
        prefix=f"{offerers_factories.DEFAULT_PREFIX}{other_offerer_provider.offerer.id}",
        secret=OTHER_SECRET,
    )


@pytest.fixture(name="other_token")
def other_token_fixture(other_api_key):
    return offerers_factories.build_clear_api_key(other_api_key.prefix, OTHER_SECRET)


@pytest.fixture(name="other_auth_client")
def other_auth_client(other_token, client):
    return client.with_explicit_token(other_token)
