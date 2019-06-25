from models import Provider, PcObject
from models.db import db
from repository.venue_provider_queries import find_venue_provider
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_user, create_user_offerer, create_venue, create_venue_provider


class FindVenueProviderTest:

    @clean_database
    def test_return_venue_provider_when_exists(self, app):
        # given
        provider = Provider()
        provider.name = 'Open Agenda'
        provider.localClass = 'OpenAgenda'
        provider.isActive = True
        provider.enabledForPro = True
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer, is_admin=True)
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        venue_provider = create_venue_provider(venue, provider, venue_id_at_offer_provider="775671464")
        PcObject.save(provider, user_offerer, venue, venue_provider)

        # when
        existing_venue_provider = find_venue_provider(provider.id, venue.id, "775671464")

        # then
        assert existing_venue_provider == venue_provider

        # clean
