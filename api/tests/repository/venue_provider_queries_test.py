import pytest

from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
import pcapi.core.providers.factories as providers_factories
from pcapi.repository.venue_provider_queries import get_active_venue_providers_for_specific_provider


class GetActiveVenueProvidersForSpecificProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_venue_provider_matching_provider_id(self, app):
        # Given
        offerer = OffererFactory()
        venue1 = VenueFactory(managingOfferer=offerer, siret="12345678901234")
        venue2 = VenueFactory(managingOfferer=offerer)
        titelive_provider = providers_factories.APIProviderFactory()
        allocine_provider = providers_factories.AllocineProviderFactory()
        venue_provider1 = providers_factories.VenueProviderFactory(venue=venue1, provider=titelive_provider)
        providers_factories.VenueProviderFactory(venue=venue2, provider=allocine_provider)

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
        titelive_provider = providers_factories.APIProviderFactory()
        venue_provider1 = providers_factories.VenueProviderFactory(venue=venue1, provider=titelive_provider)
        providers_factories.VenueProviderFactory(venue=venue2, provider=titelive_provider, isActive=False)

        # When
        venue_providers = get_active_venue_providers_for_specific_provider(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider1]
