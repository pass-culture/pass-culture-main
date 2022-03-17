import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_venue_provider_nOffers():
    venue = offerers_factories.VenueFactory()
    provider1 = providers_factories.ProviderFactory()
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1)
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1)
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1, isActive=False)  # not counted
    offers_factories.OfferFactory(venue=venue, lastProvider=None)  # not counted
    provider2 = providers_factories.ProviderFactory()
    offers_factories.OfferFactory(venue=venue, lastProvider=provider2)

    venue_provider1 = providers_factories.VenueProviderFactory(venue=venue, provider=provider1)
    venue_provider2 = providers_factories.VenueProviderFactory(venue=venue, provider=provider2)
    assert venue_provider1.nOffers == 2
    assert venue_provider2.nOffers == 1


@pytest.mark.usefixtures("db_session")
def test_raise_errors_if_venue_provider_already_exists_with_same_information():
    venue_provider1 = providers_factories.VenueProviderFactory()
    venue_provider2 = providers_factories.VenueProviderFactory.build(
        venue=venue_provider1.venue,
        provider=venue_provider1.provider,
        venueIdAtOfferProvider=venue_provider1.venueIdAtOfferProvider,
    )

    with pytest.raises(ApiErrors) as errors:
        repository.save(venue_provider2)
    assert errors.value.errors["global"] == ["Votre lieu est déjà lié à cette source"]


@pytest.mark.usefixtures("db_session")
def test_isFromAllocineProvider():
    allocine = providers_factories.ProviderFactory(localClass="AllocineStocks")
    allocine_venue_provider = providers_factories.VenueProviderFactory(provider=allocine)
    assert allocine_venue_provider.isFromAllocineProvider

    other = providers_factories.ProviderFactory(localClass="Dummy")
    other_venue_provider = providers_factories.VenueProviderFactory(provider=other)
    assert not other_venue_provider.isFromAllocineProvider
