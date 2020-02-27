from models import AllocineVenueProvider, VenueProvider
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, \
    create_allocine_venue_provider, \
    create_provider, create_venue_provider
from tests.model_creators.provider_creators import activate_provider


class AllocineVenueProviderTest:
    @clean_database
    def test_allocine_venue_provider_should_inherit_from_venue_provider(self, app):
        offerer = create_offerer()
        venue = create_venue(offerer)

        provider_allocine = activate_provider('AllocineStocks')

        allocine_venue_provider = create_allocine_venue_provider(venue, provider_allocine, is_duo=True)

        repository.save(allocine_venue_provider)

        assert VenueProvider.query.count() == 1
        assert AllocineVenueProvider.query.count() == 1
        allocine_vp = VenueProvider.query \
            .filter(VenueProvider.providerId == provider_allocine.id) \
            .first()
        assert isinstance(allocine_vp, AllocineVenueProvider)
        assert allocine_vp.isDuo
        assert allocine_vp.isFromAllocineProvider

    @clean_database
    def test_query_venue_provider_load_allocine_venue_provider_attributes_when_connected_to_allocine(self, app):
        offerer = create_offerer()
        venue = create_venue(offerer)

        provider_allocine = activate_provider('AllocineStocks')
        provider = create_provider(local_class='TestLocalProvider')

        venue_provider = create_venue_provider(venue, provider)

        allocine_venue_provider = create_allocine_venue_provider(venue, provider_allocine, is_duo=True)

        repository.save(venue_provider, allocine_venue_provider)

        assert VenueProvider.query.count() == 2
        assert AllocineVenueProvider.query.count() == 1
        created_venue_provider = VenueProvider.query \
            .filter(VenueProvider.providerId == provider.id) \
            .first()
        assert isinstance(created_venue_provider, VenueProvider)

        created_allocine_venue_provider = VenueProvider.query \
            .filter(VenueProvider.providerId == provider_allocine.id) \
            .first()
        assert isinstance(created_allocine_venue_provider, AllocineVenueProvider)
