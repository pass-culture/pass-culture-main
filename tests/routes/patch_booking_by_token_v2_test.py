from urllib.parse import urlencode


from models import PcObject, EventType, ThingType, Deposit, Booking, User
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_deposit, create_venue, create_offerer, \
    create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer
from tests.test_utils import create_api_key, create_stock_with_event_offer
from utils.human_ids import humanize
from utils.token import random_token

API_KEY_VALUE = random_token(64)

class Patch:
    class Returns401:
        @clean_database
        def when_user_not_logged_in_and_doesnt_give_api_key(self, app):
            # Given
            user = create_user(email='user@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(booking)

            url = '/v2/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 401

        @clean_database
        def when_user_not_logged_in_and_not_existing_api_key_given(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)

            url = '/v2/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).patch(url, headers={
                    'Authorization': 'Bearer WrongApiKey1234567',
                    'Origin': 'http://localhost'})

            # Then
            assert response.status_code == 401


    class Returns204:
        @clean_database
        def when_api_key_is_provided_and_rights_and_regular_offer(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, offerer)

            offererApiKey = create_api_key(offerer, API_KEY_VALUE)
            PcObject.save(offererApiKey)

            booking_id = booking.id
            user2ApiKey = 'Bearer ' + offererApiKey.value

            url = '/v2/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': user2ApiKey,
                    'Origin': 'http://localhost'}
            )

            # Then
            assert response.status_code == 204
            assert Booking.query.get(booking_id).isUsed is True

        @clean_database
        def when_user_is_logged_in_and_regular_offer(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            booking_id = booking.id
            url = '/v2/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 204
            assert Booking.query.get(booking_id).isUsed is True

        @clean_database
        def when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            booking_id = booking.id
            booking_token = booking.token.lower()
            url = '/v2/bookings/token/{}'.format(booking_token)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            assert response.status_code == 204
            assert Booking.query.get(booking_id).isUsed is True

        @clean_database
        def when_user_is_logged_in_expect_booking_to_be_used_with_non_standard_origin_header(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)

            booking_id = booking.id
            url = '/v2/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@email.fr') \
                .patch(url, headers={'origin': 'http://random_header.fr'})

            # Then
            assert response.status_code == 204
            assert Booking.query.get(booking_id).isUsed is True

        @clean_database
        def when_user_is_logged_in_expect_booking_to_be_used_with_special_char_in_url(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            user_admin = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(user_offerer, booking)
            url_email = urlencode({'email': 'user+plus@email.fr'})
            url = '/v2/bookings/token/{}?{}'.format(booking.token, url_email)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)
            # Then
            assert response.status_code == 204

        @clean_database
        def when_admin_user_is_logged_in_expect_activation_booking_to_be_used_and_linked_user_to_be_able_to_book(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_offer_with_event_product(venue, event_type=ThingType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)
            user_id = user.id
            url = '/v2/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            user = User.query.get(user_id)
            assert response.status_code == 204
            assert user.canBookFreeOffers is True
            assert user.deposits[0].amount == 500

        # when_activation_event_and_user_has_rights


