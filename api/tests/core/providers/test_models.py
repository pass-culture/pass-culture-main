import pytest

import pcapi.utils.repository as db_repository
from pcapi.core.providers import factories
from pcapi.models.api_errors import ApiErrors


pytestmark = pytest.mark.usefixtures("db_session")


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
    allocine = factories.AllocineProviderFactory()
    allocine_venue_provider = factories.VenueProviderFactory(provider=allocine)
    assert allocine_venue_provider.isFromAllocineProvider

    other = factories.ProviderFactory(localClass="Dummy")
    other_venue_provider = factories.VenueProviderFactory(provider=other)
    assert not other_venue_provider.isFromAllocineProvider
