import pytest

from pcapi.core.offerers.factories import APIProviderFactory
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import VenueProvider
from pcapi.model_creators.generic_creators import create_allocine_venue_provider
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.repository import repository
from pcapi.repository.venue_provider_queries import get_active_venue_providers_for_specific_provider
from pcapi.repository.venue_provider_queries import get_venue_provider_by_id


class GetActiveVenueProvidersForSpecificProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_venue_provider_matching_provider_id(self, app):
        # Given
        offerer = create_offerer()
        venue1 = create_venue(offerer, siret="12345678901234")
        venue2 = create_venue(offerer)
        titelive_provider = APIProviderFactory()
        allocine_provider = activate_provider("AllocineStocks")
        venue_provider1 = create_venue_provider(venue1, titelive_provider)
        venue_provider2 = create_venue_provider(venue2, allocine_provider)
        repository.save(venue_provider1, venue_provider2)

        # When
        venue_providers = get_active_venue_providers_for_specific_provider(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider1]

    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_active_venue_providers_matching_provider_id(self, app):
        # Given
        offerer = create_offerer()
        venue1 = create_venue(offerer, siret="12345678901234")
        venue2 = create_venue(offerer)
        titelive_provider = APIProviderFactory()
        venue_provider1 = create_venue_provider(venue1, titelive_provider)
        venue_provider2 = create_venue_provider(venue2, titelive_provider, is_active=False)
        repository.save(venue_provider1, venue_provider2)

        # When
        venue_providers = get_active_venue_providers_for_specific_provider(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider1]


class GetVenueProviderByIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_matching_venue_provider(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        titelive_provider = APIProviderFactory()
        venue_provider = create_venue_provider(venue, titelive_provider)
        repository.save(venue_provider)

        # When
        existing_venue_provider = get_venue_provider_by_id(venue_provider.id)

        # Then
        assert existing_venue_provider == venue_provider
        assert isinstance(venue_provider, VenueProvider)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_matching_venue_provider_with_allocine_attributes(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        titelive_provider = activate_provider("AllocineStocks")
        venue_provider = create_allocine_venue_provider(venue, titelive_provider)
        repository.save(venue_provider)

        # When
        existing_venue_provider = get_venue_provider_by_id(venue_provider.id)

        # Then
        assert existing_venue_provider == venue_provider
        assert isinstance(venue_provider, AllocineVenueProvider)
