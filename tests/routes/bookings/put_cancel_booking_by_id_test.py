from datetime import datetime, timedelta
from unittest.mock import patch

from models import BookingSQLEntity
from repository import repository
from tests.conftest import TestClient
import pytest
from tests.model_creators.generic_creators import create_booking, \
    create_deposit, create_offerer, create_user, create_venue, create_stock
from tests.model_creators.specific_creators import create_offer_with_event_product
from utils.human_ids import humanize


class Put:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def expect_the_booking_to_be_cancelled_by_current_user(self, app):
            # Given
            in_four_days = datetime.utcnow() + timedelta(days=4)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(beginning_datetime=in_four_days, offer=offer)
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
            assert response.json == {'amount': 10.0,
                                     'completedUrl': None,
                                     'id': humanize(booking.id),
                                     'isCancelled': True,
                                     'quantity': booking.quantity,
                                     'stock': {'price': 10.0},
                                     'stockId': humanize(stock.id),
                                     'token': booking.token,
                                     'user': {'id': humanize(user.id), 'wallet_balance': 500.0}
                                     }

        @patch('routes.bookings.feature_queries.is_active', return_value=True)
        @patch('routes.bookings.redis.add_offer_id')
        @pytest.mark.usefixtures("db_session")
        def when_booking_expect_offer_id_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
            user = create_user(email='test2@example.com')
            booking = create_booking(user)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 200
            mock_add_offer_id_to_redis.assert_called_once_with(client=app.redis_client, offer_id=booking.stock.offerId)

        @patch('routes.bookings.feature_queries.is_active', return_value=False)
        @patch('routes.bookings.redis.add_offer_id')
        @pytest.mark.usefixtures("db_session")
        def when_booking_expect_offer_id_not_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
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

    class Returns400:
        @pytest.mark.usefixtures("db_session")
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

        @pytest.mark.usefixtures("db_session")
        def when_event_beginning_date_time_is_in_less_than_72_hours(self, app):
            # Given
            tomorrow = datetime.utcnow() + timedelta(days=1)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(beginning_datetime=tomorrow, offer=offer)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .put(f'/bookings/{humanize(booking.id)}/cancel')

            # Then
            assert response.status_code == 400
            assert response.json['booking'] == [
                "Impossible d'annuler une réservation moins de 72h avant le début de l'évènement"]

    class Returns404:
        @pytest.mark.usefixtures("db_session")
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
            assert response.status_code == 404
            assert not BookingSQLEntity.query.get(booking.id).isCancelled

        @pytest.mark.usefixtures("db_session")
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
