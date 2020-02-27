from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_venue_provider, \
    create_allocine_venue_provider
from utils.human_ids import humanize
from utils.logger import logger


class Get:
    class Returns200:
        @clean_database
        def when_listing_all_venues_with_a_valid_venue_id(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = get_provider_by_local_class('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            repository.save(venue_provider)

            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # when
            response = auth_request.get('/venueProviders?venueId=' + humanize(venue.id))

            # then
            assert response.status_code == 200
            assert response.json[0].get('id') == humanize(venue_provider.id)
            assert response.json[0].get('venueId') == humanize(venue.id)

        @clean_database
        def when_listing_all_allocine_venues_with_a_valid_venue_id(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            titelive_things_provider = get_provider_by_local_class('AllocineStocks')
            allocine_venue_provider = create_allocine_venue_provider(venue, titelive_things_provider)
            repository.save(allocine_venue_provider)

            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # when
            response = auth_request.get('/venueProviders?venueId=' + humanize(venue.id))

            # then
            assert response.status_code == 200
            logger.info(response.json)
            assert response.json[0].get('id') == humanize(allocine_venue_provider.id)
            assert response.json[0].get('venueId') == humanize(venue.id)

    class Returns400:
        @clean_database
        def when_listing_all_venues_without_venue_id_argument(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = get_provider_by_local_class('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            repository.save(venue_provider)

            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # when
            response = auth_request.get('/venueProviders')

            # then
            assert response.status_code == 400
