from models import AllocineVenueProvider, VenueProvider
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_venue_provider
from tests.model_creators.provider_creators import activate_provider


class AllocineVenueProviderTest:
    @clean_database
    def test_allocine_venue_provider_should_inherit_from_venue_provider(self, app):
        offerer = create_offerer()
        venue = create_venue(offerer)

        provider_allocine = activate_provider('AllocineStocks')

        allocine_venue_provider = AllocineVenueProvider()
        allocine_venue_provider.provider = provider_allocine
        allocine_venue_provider.venue = venue
        allocine_venue_provider.isDuo = True

        repository.save(allocine_venue_provider)

        assert AllocineVenueProvider.query.count() == 1
        assert VenueProvider.query.count() == 1
        allocine_vp = VenueProvider.query.filter(VenueProvider.providerId == provider_allocine.id).first()
        assert allocine_vp.isDuo
        assert allocine_vp.providerClass == 'AllocineStocks'
