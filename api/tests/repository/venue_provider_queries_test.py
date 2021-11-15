import pytest

from pcapi.core.offerers.factories import APIProviderFactory
from pcapi.core.offerers.factories import AllocineVenueProviderFactory
from pcapi.core.offerers.factories import VenueProviderFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import VenueProvider
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.repository.venue_provider_queries import get_active_venue_providers_for_specific_provider
from pcapi.repository.venue_provider_queries import get_venue_provider_by_id


class GetActiveVenueProvidersForSpecificProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_venue_provider_matching_provider_id(self, app):
        # Given
        offerer = OffererFactory()
        venue1 = VenueFactory(managingOfferer=offerer, siret="12345678901234")
        venue2 = VenueFactory(managingOfferer=offerer)
        titelive_provider = APIProviderFactory()
        allocine_provider = activate_provider("AllocineStocks")
        venue_provider1 = VenueProviderFactory(venue=venue1, provider=titelive_provider)
        VenueProviderFactory(venue=venue2, provider=allocine_provider)

        # When
        venue_providers = get_active_venue_providers_for_specific_provider(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider1]

    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_active_venue_providers_matching_provider_id(self, app):
        # Given
        offerer = OffererFactory()
        venue1 = VenueFactory(managingOfferer=offerer, siret="12345678901234")
        venue2 = VenueFactory(managingOfferer=offerer)
        titelive_provider = APIProviderFactory()
        venue_provider1 = VenueProviderFactory(venue=venue1, provider=titelive_provider)
        VenueProviderFactory(venue=venue2, provider=titelive_provider, isActive=False)

        # When
        venue_providers = get_active_venue_providers_for_specific_provider(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider1]


class GetVenueProviderByIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_matching_venue_provider(self):
        # Given
        titelive_provider = APIProviderFactory()
        venue_provider = VenueProviderFactory(provider=titelive_provider)

        # When
        existing_venue_provider = get_venue_provider_by_id(venue_provider.id)

        # Then
        assert existing_venue_provider == venue_provider
        assert isinstance(venue_provider, VenueProvider)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_matching_venue_provider_with_allocine_attributes(self):
        # Given
        allocine_venue_provider = AllocineVenueProviderFactory()

        # When
        existing_venue_provider = get_venue_provider_by_id(allocine_venue_provider.id)

        # Then
        assert existing_venue_provider == allocine_venue_provider
        assert isinstance(allocine_venue_provider, AllocineVenueProvider)
