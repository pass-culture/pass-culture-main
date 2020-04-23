from datetime import datetime, timedelta
from unittest.mock import patch

from models import BookingSQLEntity, Offerer
from repository import repository
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_booking, \
    create_deposit, create_offerer, create_user, create_venue, create_user_offerer
from tests.model_creators.specific_creators import create_event_occurrence, \
    create_offer_with_event_product, \
    create_stock_from_event_occurrence
from utils.human_ids import humanize


class Put:
    class Returns200:
        @clean_database
        def expect_the_booking_to_have_good_includes(self, app):
            # Given
            in_four_days = datetime.utcnow() + timedelta(days=4)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=in_four_days)
            stock = create_stock_from_event_occurrence(event_occurrence)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

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
            event_occurrence = create_event_occurrence(offer, beginning_datetime=in_four_days)
            stock = create_stock_from_event_occurrence(event_occurrence)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 200
            assert BookingSQLEntity.query.get(booking.id).isCancelled
            print('send email ?)')

        @clean_database
        def expect_the_booking_to_be_cancelled_by_admin_for_someone_else(self, app):
            # Given
            admin_user = create_user(can_book_free_offers=False, is_admin=True)
            other_user = create_user(email='test2@example.com')
            booking = create_booking(other_user)
            create_deposit(other_user, amount=500)
            repository.save(admin_user, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(admin_user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 200
            assert BookingSQLEntity.query.get(booking.id).isCancelled

        @patch('routes.bookings.feature_queries.is_active', return_value=True)
        @patch('routes.bookings.redis.add_offer_id')
        @clean_database
        def when_booking_expect_offer_id_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
            admin_user = create_user(can_book_free_offers=False, is_admin=True)
            other_user = create_user(email='test2@example.com')

            booking = create_booking(other_user)
            create_deposit(other_user, amount=500)
            repository.save(admin_user, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(admin_user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 200
            mock_add_offer_id_to_redis.assert_called_once_with(client=app.redis_client, offer_id=booking.stock.offerId)

        @patch('routes.bookings.feature_queries.is_active', return_value=False)
        @patch('routes.bookings.redis.add_offer_id')
        @clean_database
        def when_booking_expect_offer_id_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
            admin_user = create_user(can_book_free_offers=False, is_admin=True)
            other_user = create_user(email='test2@example.com')

            booking = create_booking(other_user)
            create_deposit(other_user, amount=500)
            repository.save(admin_user, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(admin_user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            mock_add_offer_id_to_redis.assert_not_called()

        @clean_database
        @patch('routes.bookings.send_booking_cancellation_emails_to_user_and_offerer', return_value=True)
        @patch('routes.bookings.send_raw_email', return_value=True)
        def when_cancel_by_offerer_should_send_email_to_beneficiary_user(self,
                                                                         mock_send_raw_email,
                                                                         mock_send_booking_cancellation_emails_to_user_and_offerer,
                                                                         app):
            # Given
            offerer_user = create_user(can_book_free_offers=False, is_admin=False)
            beneficiary_user = create_user(email='test2@example.com')
            booking = create_booking(beneficiary_user)
            create_deposit(beneficiary_user, amount=500)
            repository.save(booking, offerer_user)

            booking_offerer_id = booking.stock.offer.venue.managingOffererId
            offerer = Offerer.query.filter_by(id=booking_offerer_id).first()

            user_offerer = create_user_offerer(offerer_user, offerer)

            repository.save(user_offerer)

            is_offerer_cancellation = True
            is_user_cancellation = False

            # When
            response = TestClient(app.test_client()) \
                .with_auth(offerer_user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 200
            mock_send_booking_cancellation_emails_to_user_and_offerer.assert_called_once_with(booking,
                                                                                              is_offerer_cancellation,
                                                                                              is_user_cancellation,
                                                                                              mock_send_raw_email)

        @clean_database
        @patch('routes.bookings.send_booking_cancellation_emails_to_user_and_offerer', return_value=True)
        @patch('routes.bookings.send_raw_email', return_value=True)
        def when_cancel_by_beneficiary_should_send_email_to_offerer_user(self,
                                                                         mock_send_raw_email,
                                                                         mock_send_booking_cancellation_emails_to_user_and_offerer,
                                                                         app):
            # Given
            offerer_user = create_user(can_book_free_offers=False, is_admin=False)
            beneficiary_user = create_user(email='test2@example.com')
            booking = create_booking(beneficiary_user)
            create_deposit(beneficiary_user, amount=500)
            repository.save(booking, offerer_user)

            booking_offerer_id = booking.stock.offer.venue.managingOffererId
            offerer = Offerer.query.filter_by(id=booking_offerer_id).first()

            user_offerer = create_user_offerer(offerer_user, offerer)

            repository.save(user_offerer)

            is_offerer_cancellation = False
            is_user_cancellation = True

            # When
            response = TestClient(app.test_client()) \
                .with_auth(beneficiary_user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 200
            mock_send_booking_cancellation_emails_to_user_and_offerer.assert_called_once_with(booking,
                                                                                              is_offerer_cancellation,
                                                                                              is_user_cancellation,
                                                                                              mock_send_raw_email)

    class Returns204:
        @clean_database
        def when_trying_cancel_an_already_cancelled_booking(self, app):
            # Given
            user = create_user()
            booking = create_booking(user=user, is_cancelled=True)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 204
            assert BookingSQLEntity.query.get(booking.id).isCancelled

    class Returns400:
        @clean_database
        def when_the_booking_cannot_be_cancelled(self, app):
            # Given
            user = create_user()
            booking = create_booking(user=user, is_used=True)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 400
            assert response.json['booking'] == ["Impossible d'annuler une réservation consommée"]
            assert not BookingSQLEntity.query.get(booking.id).isCancelled

        @clean_database
        def when_event_beginning_date_time_is_in_less_than_72_hours(self, app):
            # Given
            in_five_days = datetime.utcnow() + timedelta(days=5)
            in_one_days = datetime.utcnow() + timedelta(days=1)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=in_one_days)
            stock = create_stock_from_event_occurrence(event_occurrence)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

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
            repository.save(user, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 403
            assert not BookingSQLEntity.query.get(booking.id).isCancelled

    class Returns404:
        @clean_database
        def when_the_booking_does_not_exist(self, app):
            # Given
            user = create_user()
            repository.save(user)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put('/bookings/AX/cancel')

            # Then
            assert response.status_code == 404
