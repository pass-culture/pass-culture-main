from models import AllocineVenueProvider, VenueProvider
from repository import repository
from repository.venue_provider_queries import get_venue_providers_to_sync, get_nb_containers_at_work, \
    get_venue_provider_by_id, get_active_venue_providers_for_specific_provider
from tests.conftest import clean_database
from model_creators.generic_creators import create_offerer, create_venue, create_venue_provider, \
    create_allocine_venue_provider
from model_creators.provider_creators import activate_provider


class GetActiveVenueProvidersForSpecificProviderTest:
    @clean_database
    def test_should_return_all_venue_provider_matching_provider_id(self, app):
        # Given
        offerer = create_offerer()
        venue1 = create_venue(offerer, siret='12345678901234')
        venue2 = create_venue(offerer)
        titelive_provider = activate_provider('TiteLiveStocks')
        allocine_provider = activate_provider('AllocineStocks')
        venue_provider1 = create_venue_provider(venue1, titelive_provider)
        venue_provider2 = create_venue_provider(venue2, allocine_provider)
        repository.save(venue_provider1, venue_provider2)

        # When
        venue_providers = get_active_venue_providers_for_specific_provider(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider1]

    @clean_database
    def test_should_return_all_active_venue_providers_matching_provider_id(self, app):
        # Given
        offerer = create_offerer()
        venue1 = create_venue(offerer, siret='12345678901234')
        venue2 = create_venue(offerer)
        titelive_provider = activate_provider('TiteLiveStocks')
        venue_provider1 = create_venue_provider(venue1, titelive_provider)
        venue_provider2 = create_venue_provider(venue2, titelive_provider, is_active=False)
        repository.save(venue_provider1, venue_provider2)

        # When
        venue_providers = get_active_venue_providers_for_specific_provider(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider1]


class GetVenueProvidersToSyncTest:
    @clean_database
    def test_should_return_only_venue_provider_for_specified_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        titelive_provider = activate_provider('TiteLiveStocks')
        allocine_provider = activate_provider('AllocineStocks')
        venue_provider_titelive = create_venue_provider(venue, titelive_provider)
        venue_provider_allocine = create_venue_provider(venue, allocine_provider)
        repository.save(venue_provider_titelive, venue_provider_allocine)

        # When
        venue_providers = get_venue_providers_to_sync(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider_titelive]

    @clean_database
    def test_should_return_venue_provider_with_no_worker_id(self, app):
        # Given
        offerer = create_offerer()
        venue_1 = create_venue(offerer, siret='12345678901234')
        venue_2 = create_venue(offerer)
        titelive_provider = activate_provider('TiteLiveStocks')
        venue_provider_1 = create_venue_provider(venue_1, titelive_provider, last_sync_date=None, sync_worker_id=None)
        venue_provider_2 = create_venue_provider(venue_2, titelive_provider, last_sync_date=None,
                                                 sync_worker_id='123456789098765432345634')
        repository.save(venue_provider_1, venue_provider_2)

        # When
        venue_providers = get_venue_providers_to_sync(titelive_provider.id)

        # Then
        assert venue_providers == [venue_provider_1]


class GetNbContainersAtWorkTest:
    @clean_database
    def test_should_return_number_of_venue_provider_with_worker_id(self, app):
        # Given
        offerer = create_offerer()
        venue_1 = create_venue(offerer, siret='12345678901234')
        venue_2 = create_venue(offerer)
        titelive_provider = activate_provider('TiteLiveStocks')
        venue_provider_1 = create_venue_provider(venue_1, titelive_provider)
        venue_provider_2 = create_venue_provider(venue_2, titelive_provider, sync_worker_id='1234567')
        repository.save(venue_provider_1, venue_provider_2)

        # When
        nb_containers_at_work = get_nb_containers_at_work()

        # Then
        assert nb_containers_at_work == 1


class GetVenueProviderByIdTest:
    @clean_database
    def test_should_return_matching_venue_provider(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        titelive_provider = activate_provider('TiteLiveStocks')
        venue_provider = create_venue_provider(venue, titelive_provider)
        repository.save(venue_provider)

        # When
        existing_venue_provider = get_venue_provider_by_id(venue_provider.id)

        # Then
        assert existing_venue_provider == venue_provider
        assert isinstance(venue_provider, VenueProvider)

    @clean_database
    def test_should_return_matching_venue_provider_with_allocine_attributes(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        titelive_provider = activate_provider('AllocineStocks')
        venue_provider = create_allocine_venue_provider(venue, titelive_provider)
        repository.save(venue_provider)

        # When
        existing_venue_provider = get_venue_provider_by_id(venue_provider.id)

        # Then
        assert existing_venue_provider == venue_provider
        assert isinstance(venue_provider, AllocineVenueProvider)
