import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.providers import factories
from pcapi.models.api_errors import ApiErrors
import pcapi.repository.repository as db_repository


pytestmark = pytest.mark.usefixtures("db_session")


def test_venue_provider_nOffers():
    venue = offerers_factories.VenueFactory()
    provider1 = factories.ProviderFactory()
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1)
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1)
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1, isActive=False)  # not counted
    offers_factories.OfferFactory(venue=venue, lastProvider=None)  # not counted
    provider2 = factories.ProviderFactory()
    offers_factories.OfferFactory(venue=venue, lastProvider=provider2)

    venue_provider1 = factories.VenueProviderFactory(venue=venue, provider=provider1)
    venue_provider2 = factories.VenueProviderFactory(venue=venue, provider=provider2)
    assert venue_provider1.nOffers == 2
    assert venue_provider2.nOffers == 1


def test_raise_errors_if_venue_provider_already_exists_with_same_information():
    venue_provider1 = factories.VenueProviderFactory()
    venue_provider2 = factories.VenueProviderFactory.build(
        venue=venue_provider1.venue,
        provider=venue_provider1.provider,
        venueIdAtOfferProvider=venue_provider1.venueIdAtOfferProvider,
    )

    with pytest.raises(ApiErrors) as errors:
        db_repository.save(venue_provider2)
    assert errors.value.errors["global"] == ["Votre lieu est déjà lié à cette source"]


def test_isFromAllocineProvider():
    allocine = factories.ProviderFactory(localClass="AllocineStocks")
    allocine_venue_provider = factories.VenueProviderFactory(provider=allocine)
    assert allocine_venue_provider.isFromAllocineProvider

    other = factories.ProviderFactory(localClass="Dummy")
    other_venue_provider = factories.VenueProviderFactory(provider=other)
    assert not other_venue_provider.isFromAllocineProvider
