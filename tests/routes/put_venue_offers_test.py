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

API_URL = '/venues/'


class Put:
    class Returns401:
        @clean_database
        def test_user_not_logged_in(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence1 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            PcObject.save(
                stock1, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/activate'

            # when
            response = TestClient(app.test_client()).put(api_url)

            # then
            assert response.status_code == 401

        @clean_database
        def test_user_is_not_venue_managing_offerer(self, app):
            # Given
            user = create_user(email='test@email.com')
            user2 = create_user(email='test2@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence1 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            PcObject.save(
                stock1, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/activate'

            # When
            response = TestClient(app.test_client()).with_auth('test2@email.com') \
            .put(api_url)

            # Then
            assert response.status_code == 401


    class Returns404:
        @clean_database
        def test_venue_does_not_exist(self, app):
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

            api_url = API_URL + '6TT67RTE/offers/activate'

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com') \
            .put(api_url)

            # Then
            assert response.status_code == 404


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

            api_url = API_URL + humanize(venue.id) + '/offers/activate'

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com') \
            .put(api_url)

            # Then
            assert response.status_code == 200
            assert response.json[0]['isActive'] == True
            assert response.json[1]['isActive'] == True


        @clean_database
        def test_deactivate_all_venue_offers(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            event_occurrence1 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            PcObject.save(
                offer2, stock1, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/deactivate'

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com') \
            .put(api_url)

            # Then
            assert response.status_code == 200
            assert response.json[0]['isActive'] == False
            assert response.json[1]['isActive'] == False
