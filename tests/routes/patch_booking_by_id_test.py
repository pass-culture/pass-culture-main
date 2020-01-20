from datetime import datetime, timedelta
from unittest.mock import patch

from models import Booking, PcObject
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_booking, \
    create_deposit, create_offerer, create_user, create_venue
from tests.model_creators.specific_creators import create_event_occurrence, \
    create_offer_with_event_product, \
    create_stock_from_event_occurrence
from utils.human_ids import humanize


class Patch:
    class Returns200:
        @clean_database
        def expect_the_booking_to_have_good_includes(self, app):
            # Given
            in_four_days = datetime.utcnow() + timedelta(days=4)
            in_five_days = datetime.utcnow() + timedelta(days=5)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=in_four_days,
                                                       end_datetime=in_five_days)
            stock = create_stock_from_event_occurrence(event_occurrence)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            PcObject.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': True})

            # Then
            assert response.status_code == 200
            assert response.json['stock']['isBookable']

        @clean_database
        def expect_the_booking_to_be_cancelled_by_current_user(self, app):
            # Given
            in_four_days = datetime.utcnow() + timedelta(days=4)
            in_five_days = datetime.utcnow() + timedelta(days=5)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=in_four_days,
                                                       end_datetime=in_five_days)
            stock = create_stock_from_event_occurrence(event_occurrence)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            PcObject.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': True})

            # Then
            assert response.status_code == 200
            assert Booking.query.get(booking.id).isCancelled

        @clean_database
        def expect_the_booking_to_be_cancelled_by_admin_for_someone_else(self, app):
            # Given
            admin_user = create_user(can_book_free_offers=False, is_admin=True)
            other_user = create_user(email='test2@example.com')
            booking = create_booking(other_user)
            create_deposit(other_user, amount=500)
            PcObject.save(admin_user, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(admin_user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': True})

            # Then
            assert response.status_code == 200
            assert Booking.query.get(booking.id).isCancelled

        @patch('routes.bookings.redis.add_offer_id')
        @clean_database
        def when_booking_expect_offer_id_to_be_added_to_redis(self, mock_add_offer_id_to_redis, app):
            # Given
            admin_user = create_user(can_book_free_offers=False, is_admin=True)
            other_user = create_user(email='test2@example.com')
            booking = create_booking(other_user)
            create_deposit(other_user, amount=500)
            PcObject.save(admin_user, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(admin_user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': True})

            # Then
            assert response.status_code == 200
            mock_add_offer_id_to_redis.assert_called_once_with(client=app.redis_client, offer_id=booking.stock.offerId)

    class Returns400:
        @clean_database
        def when_the_booking_cannot_be_cancelled(self, app):
            # Given
            user = create_user()
            booking = create_booking(user=user, is_used=True)
            create_deposit(user, amount=500)
            PcObject.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': True})

            # Then
            assert response.status_code == 400
            assert response.json['booking'] == ["Impossible d'annuler une réservation consommée"]
            assert not Booking.query.get(booking.id).isCancelled

        @clean_database
        def when_trying_to_patch_something_else_than_is_cancelled(self, app):
            # Given
            user = create_user()
            booking = create_booking(user=user, quantity=1)
            create_deposit(user, amount=500)
            PcObject.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'quantity': 3})

            # Then
            assert response.status_code == 400
            assert booking.quantity == 1

        @clean_database
        def when_trying_to_revert_cancellation(self, app):
            # Given
            user = create_user()
            booking = create_booking(user=user, is_cancelled=True)
            create_deposit(user, amount=500)
            PcObject.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': False})

            # Then
            assert response.status_code == 400
            assert Booking.query.get(booking.id).isCancelled

        @clean_database
        def when_event_beginning_date_time_is_in_less_than_72_hours(self, app):
            # Given
            in_five_days = datetime.utcnow() + timedelta(days=5)
            in_one_days = datetime.utcnow() + timedelta(days=1)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=in_one_days, end_datetime=in_five_days)
            stock = create_stock_from_event_occurrence(event_occurrence)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            PcObject.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': True})

            # Then
            assert response.status_code == 400

    class Returns403:
        @clean_database
        def when_cancelling_a_booking_of_someone_else(self, app):
            # Given
            other_user = create_user(email='test2@example.com')
            booking = create_booking(other_user)
            user = create_user()
            create_deposit(other_user, amount=500)
            PcObject.save(user, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch(f'/bookings/{humanize(booking.id)}', json={'isCancelled': True})

            # Then
            assert response.status_code == 403
            assert not Booking.query.get(booking.id).isCancelled

    class Returns404:
        @clean_database
        def when_the_booking_does_not_exist(self, app):
            # Given
            user = create_user()
            PcObject.save(user)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch('/bookings/AX', json={'isCancelled': True})

            # Then
            assert response.status_code == 404
