from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_event_occurrence, \
    create_offer_with_event_product, \
    create_offerer, \
    create_stock_from_event_occurrence, \
    create_user, \
    create_user_offerer, \
    create_venue, \
    create_offer_with_thing_product
from utils.human_ids import humanize

API_URL = '/venues'


class Put:
    class Returns401:
        def when_activate_and_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).put(
                ACTIVATE_OFFERS_URL,
                headers={'origin': 'http://localhost:3000'}
            )

            # then
            assert response.status_code == 401


    class Returns200:
        @clean_database
        def test_activate_all_venue_offers(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            event_occurrence1 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            offer.isActive = False
            offer2.isActive = False
            PcObject.save(
                offer2, stock1, user_offerer, venue
            )

            api_url = API_URL + '?venueId=' + humanize(venue.id) + '&action=validate_offers'

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com') \
            .put(api_url)

            # Then
            assert response.status_code == 200
            assert response.json[0]['isActive'] == True
            assert response.json[1]['isActive'] == True
