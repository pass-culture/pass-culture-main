import pytest

from models import PcObject, Provider
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offerer, create_venue, create_user, create_venue_provider
from utils.human_ids import humanize
from utils.logger import logger


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_listing_all_venues_with_a_valid_venue_id(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venueProviders?venueId=' + humanize(venue.id))

            # then
            assert response.status_code == 200
            logger.info(response.json)
            assert response.json()[0].get('id') == humanize(venue_provider.id)
            assert response.json()[0].get('venueId') == humanize(venue.id)

    class Returns400:
        @clean_database
        def when_listing_all_venues_without_venue_id_argument(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venueProviders')

            # then
            assert response.status_code == 400
