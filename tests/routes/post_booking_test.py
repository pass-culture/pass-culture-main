from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from domain.booking.booking_exceptions import StockIsNotBookable
from repository import repository
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_deposit, \
    create_offerer, \
    create_recommendation, \
    create_user, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, \
    create_stock_with_event_offer, \
    create_stock_with_thing_offer
from utils.human_ids import humanize


class Post:
    class Returns201:
        @clean_database
        @patch('routes.bookings.feature_queries.is_active')
        def expect_the_booking_to_have_good_includes_when_qr_code_feature_is_off(self, qr_code_is_active, app):
            # Given
            qr_code_is_active.return_value=False
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            ok_stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0,
                                                     booking_limit_datetime=datetime.utcnow() + timedelta(minutes=2))
            user = create_user()
            recommendation = create_recommendation(offer=ok_stock.offer, user=user)
            repository.save(ok_stock, user)

            booking_json = {
                'stockId': humanize(ok_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201
            assert response.json['stock']['isBookable']
            assert 'qrCode' not in response.json.keys()

        @patch('routes.bookings.feature_queries.is_active')
        @clean_database
        def expect_the_booking_to_have_good_includes_when_qr_code_feature_is_on(self, qr_code_is_active, app):
            # Given
            qr_code_is_active.return_value=True
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            ok_stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0,
                                                     booking_limit_datetime=datetime.utcnow() + timedelta(minutes=2))
            user = create_user()
            recommendation = create_recommendation(offer=ok_stock.offer, user=user)
            repository.save(ok_stock, user)

            booking_json = {
                'stockId': humanize(ok_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201
            assert response.json['stock']['isBookable']
            assert response.json['qrCode'] is not None

        @patch('routes.bookings.feature_queries.is_active')
        @patch('routes.bookings.redis.add_offer_id')
        @clean_database
        def when_booking_expect_offer_id_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
            mock_feature.return_value=True
            beneficiary = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            thing_stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            recommendation = create_recommendation(thing_offer, beneficiary)
            create_deposit(beneficiary)
            repository.save(recommendation)

            booking_json = {
                'stockId': humanize(thing_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(beneficiary.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201
            mock_add_offer_id_to_redis.assert_called_once_with(client=app.redis_client, offer_id=thing_stock.offerId)

        @patch('routes.bookings.feature_queries.is_active')
        @patch('routes.bookings.redis.add_offer_id')
        @clean_database
        def when_booking_expect_offer_id_not_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
            mock_feature.return_value=False
            beneficiary = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            thing_stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            recommendation = create_recommendation(thing_offer, beneficiary)
            create_deposit(beneficiary)
            repository.save(recommendation)

            booking_json = {
                'stockId': humanize(thing_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            TestClient(app.test_client()) \
                .with_auth(beneficiary.email) \
                .post('/bookings', json=booking_json)

            # Then
            mock_add_offer_id_to_redis.assert_not_called()

    class Returns400:
        @clean_database
        @patch('routes.bookings.book_an_offer')
        def when_use_case_raise_stock_is_not_bookable_exception(self, mock_book_an_offer, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue)
            create_deposit(user)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            mock_book_an_offer.execute = MagicMock()
            mock_book_an_offer.execute.side_effect = StockIsNotBookable

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]
