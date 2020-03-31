from datetime import datetime, timedelta
from unittest.mock import patch

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
        def expect_the_booking_to_have_good_includes(self, app):
            # Given
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

        @patch('routes.bookings.feature_queries.is_active', return_value=True)
        @patch('routes.bookings.redis.add_offer_id')
        @clean_database
        def when_booking_expect_offer_id_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
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

        @patch('routes.bookings.feature_queries.is_active', return_value=False)
        @patch('routes.bookings.redis.add_offer_id')
        @clean_database
        def when_booking_expect_offer_id_not_to_be_added_to_redis(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
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
        def when_missing_stock_id(self, app):
            # Given
            user = create_user()
            repository.save(user)

            booking_json = {
                'stockId': None,
                'recommendationId': 'AFQA',
                'quantity': 2
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stockId'] == ['Vous devez préciser un identifiant d\'offre']

        @clean_database
        def when_missing_quantity(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            repository.save(user, stock)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': 'AFQA',
                'quantity': None
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['quantity'] == [
                "Vous devez réserver une place ou deux dans le cas d'une offre DUO."]
