from models import PcObject, Provider
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offerer, create_venue, create_user, create_venue_provider
from utils.human_ids import humanize


class Delete:
    class Returns200:
        @clean_database
        def when_venue_provider_exists(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.delete(API_URL + '/venueProviders/' + humanize(venue_provider.id))

            # then
            assert response.status_code == 200

    class Returns404:
        @clean_database
        def when_venue_provider_does_not_exist(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.delete(API_URL + '/venueProviders/ABCDEF')

            # then
            assert response.status_code == 404
