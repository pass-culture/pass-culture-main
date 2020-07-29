from unittest.mock import patch

from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_stock
from tests.model_creators.specific_creators import create_stock_with_thing_offer, create_offer_with_thing_product


class Get:
    class Returns200:
        @patch('routes.bookings.feature_queries.is_active', return_value=False)
        @clean_database
        def when_user_has_bookings_and_qr_code_feature_is_off_does_not_return_qr_code(self, qr_code_is_active, app):
            # Given
            user1 = create_user(email='user1+plus@example.com')
            user2 = create_user(email='user2+plus@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock(offer=offer, price=0)
            offer2 = create_offer_with_thing_product(venue)
            stock2 = create_stock(offer=offer2, price=0)
            booking1 = create_booking(user=user1, stock=stock, token='ABCDEF', venue=venue)
            booking2 = create_booking(user=user2, stock=stock, token='GHIJK', venue=venue)
            booking3 = create_booking(user=user1, stock=stock2, token='BBBBB', venue=venue)

            repository.save(booking1, booking2, booking3)

            # When
            response = TestClient(app.test_client()).with_auth(
                user1.email).get('/bookings')

            # Then
            all_bookings = response.json
            first_booking = all_bookings[0]
            assert response.status_code == 200
            assert len(all_bookings) == 2
            assert 'qrCode' not in first_booking
            assert 'completedUrl' in first_booking
            assert 'isEventExpired' in first_booking
            assert 'offer' in first_booking['stock']
            assert 'isEventExpired' in first_booking['stock']
            assert 'isDigital' in first_booking['stock']['offer']
            assert 'isEvent' in first_booking['stock']['offer']
            assert 'isFullyBooked' in first_booking['stock']['offer']
            assert 'offerType' in first_booking['stock']['offer']
            assert 'product' in first_booking['stock']['offer']
            assert 'thumb_url' in first_booking['stock']['offer']
            assert 'stocks' in first_booking['stock']['offer']
            assert 'isBookable' in first_booking['stock']['offer']['stocks'][0]
            assert 'venue' in first_booking['stock']['offer']
            assert 'validationToken' not in first_booking['stock']['offer']['venue']

        @patch('routes.bookings.feature_queries.is_active', return_value=True)
        @clean_database
        def when_user_has_bookings_and_qr_code_feature_is_on(self, qr_code_is_active, app):
            # Given
            user1 = create_user(email='user1+plus@example.com')
            user2 = create_user(email='user2+plus@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, offer=offer, price=0)
            offer2 = create_offer_with_thing_product(venue)
            stock2 = create_stock_with_thing_offer(offerer=offerer, venue=venue, offer=offer2, price=0)
            booking1 = create_booking(user=user1, stock=stock, venue=venue, token='ABCDEF')
            booking2 = create_booking(user=user2, stock=stock, venue=venue, token='GHIJK')
            booking3 = create_booking(user=user1, stock=stock2, venue=venue, token='BBBBB')

            repository.save(booking1, booking2, booking3)

            # When
            response = TestClient(app.test_client()).with_auth(
                user1.email).get('/bookings')

            # Then
            all_bookings = response.json
            assert len(all_bookings) == 2
            first_booking = all_bookings[0]
            assert response.status_code == 200
            assert 'qrCode' in first_booking
            assert 'completedUrl' in first_booking
            assert 'isEventExpired' in first_booking
            assert 'offer' in first_booking['stock']
            assert 'isEventExpired' in first_booking['stock']
            assert 'isDigital' in first_booking['stock']['offer']
            assert 'isEvent' in first_booking['stock']['offer']
            assert 'isFullyBooked' in first_booking['stock']['offer']
            assert 'offerType' in first_booking['stock']['offer']
            assert 'product' in first_booking['stock']['offer']
            assert 'thumb_url' in first_booking['stock']['offer']
            assert 'stocks' in first_booking['stock']['offer']
            assert 'isBookable' in first_booking['stock']['offer']['stocks'][0]
            assert 'venue' in first_booking['stock']['offer']
            assert 'validationToken' not in first_booking['stock']['offer']['venue']
