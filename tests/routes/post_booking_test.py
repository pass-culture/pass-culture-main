from datetime import datetime, timedelta
from unittest.mock import patch

from models import EventType, Offerer, ThingType
from repository import repository
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_booking, \
    create_deposit, \
    create_mediation, \
    create_offerer, \
    create_recommendation, \
    create_user, create_venue, create_stock
from tests.model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product, \
    create_stock_with_event_offer, \
    create_stock_with_thing_offer
from utils.human_ids import humanize


class Post:
    class Returns400:
        @clean_database
        def when_non_validated_venue(self, app):
            # Given
            user = create_user()
            deposit = create_deposit(user)
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
            repository.save(stock, deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_booking_limit_datetime_has_passed(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            thing_offer = create_offer_with_thing_product(venue)
            expired_stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0,
                                                          booking_limit_datetime=datetime.utcnow() - timedelta(
                                                              seconds=1))
            user = create_user()
            recommendation = create_recommendation(thing_offer, user)
            repository.save(expired_stock)

            booking_json = {
                'stockId': humanize(expired_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_too_many_bookings(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            too_many_bookings_stock = create_stock_with_thing_offer(offerer=Offerer(), venue=venue, quantity=2)
            user = create_user()
            user2 = create_user(email='user2@example.com')
            create_deposit(user)
            create_deposit(user2)
            recommendation = create_recommendation(offer=too_many_bookings_stock.offer, user=user)
            booking = create_booking(user=user2, stock=too_many_bookings_stock, venue=venue, quantity=2)
            repository.save(booking)

            booking_json = {
                'stockId': humanize(too_many_bookings_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_user_cannot_book_free_offers_and_free_offer(self, app):
            # Given
            user = create_user(can_book_free_offers=False)
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=0)
            recommendation = create_recommendation(thing_offer, user)
            deposit = create_deposit(user)
            repository.save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert 'cannotBookFreeOffers' in response.json
            assert response.json['cannotBookFreeOffers'] == [
                'Votre compte ne vous permet pas de faire de réservation.']

        @clean_database
        def when_user_has_not_enough_credit(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=200)
            event_offer = stock.offer
            recommendation = create_recommendation(event_offer, user)
            deposit = create_deposit(user, amount=0)
            repository.save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert 'insufficientFunds' in response.json
            assert response.json['insufficientFunds'] == [
                'Le solde de votre pass est insuffisant pour réserver cette offre.']

        @clean_database
        def when_only_public_credit_and_limit_of_physical_thing_reached(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            thing_stock_price_190 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=190)
            thing_stock_price_12 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=12)
            recommendation = create_recommendation(thing_offer, user)
            create_deposit(user)
            create_booking(user=user, stock=thing_stock_price_190, venue=venue)
            repository.save(recommendation)

            booking_json = {
                'stockId': humanize(thing_stock_price_12.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['global'] == [
                'Le plafond de 200 € pour les biens culturels ne vous permet pas de réserver cette offre.']

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

        @clean_database
        def when_negative_quantity(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': -3
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['quantity'] == [
                "Vous devez réserver une place ou deux dans le cas d'une offre DUO."]

        @clean_database
        def when_offer_is_inactive(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue, is_active=False)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_offerer_is_inactive(self, app):
            # Given
            user = create_user()
            offerer = create_offerer(is_active=False)
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_stock_is_soft_deleted(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, soft_deleted=True)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_null_quantity(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 0
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['quantity'] == [
                "Vous devez réserver une place ou deux dans le cas d'une offre DUO."]

        @clean_database
        def when_quantity_is_more_than_one_and_offer_is_not_duo(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 5
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['quantity'] == [
                "Vous devez réserver une place ou deux dans le cas d'une offre DUO."]

        @clean_database
        def when_quantity_is_more_than_two_and_offer_is_duo(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 3
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['quantity'] == [
                "Vous devez réserver une place ou deux dans le cas d'une offre DUO."]

        @clean_database
        def when_event_occurrence_beginning_datetime_has_passed(self, app):
            # Given
            four_days_ago = datetime.utcnow() - timedelta(days=4)
            five_days_ago = datetime.utcnow() - timedelta(days=5)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
            stock = create_stock(beginning_datetime=five_days_ago, offer=offer)
            create_deposit(user)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_thing_booking_limit_datetime_has_expired(self, app):
            # Given
            four_days_ago = datetime.utcnow() - timedelta(days=4)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, booking_limit_datetime=four_days_ago)
            create_deposit(user)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stock'] == ["Ce stock n'est pas réservable"]

        @clean_database
        def when_already_booked_by_user(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            create_booking(user=user, stock=stock, venue=venue, is_cancelled=False)
            create_deposit(user)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 400
            assert response.json['stockId'] == ["Cette offre a déja été reservée par l'utilisateur"]

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

        @clean_database
        def when_limit_date_is_in_the_future_and_offer_is_free(self, app):
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
            booking_id = response.json['id']
            r_check = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get(f'/bookings/{booking_id}')
            created_booking_json = r_check.json
            for (key, value) in booking_json.items():
                assert created_booking_json[key] == booking_json[key]

        @clean_database
        def when_booking_limit_datetime_is_none(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, booking_limit_datetime=None)
            create_deposit(user)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201

        @clean_database
        def when_user_has_enough_credit(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            user = create_user()
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=50, quantity=1)
            recommendation = create_recommendation(thing_offer, user)
            create_deposit(user, amount=50)
            repository.save(user, stock)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201
            assert 'recommendation' in response.json
            assert 'offer' in response.json['recommendation']
            assert 'venue' in response.json['recommendation']['offer']
            assert 'validationToken' not in response.json['recommendation']['offer']['venue']

        @clean_database
        def when_user_respects_expenses_limits(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO_ABO)
            user = create_user()
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=210, quantity=1)
            recommendation = create_recommendation(thing_offer, user)
            create_deposit(user)
            repository.save(user, stock)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201

        @clean_database
        def when_user_has_enough_credit_after_cancelling_booking(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=50, quantity=1)
            recommendation = create_recommendation(stock.offer, user)
            create_mediation(stock.offer)
            create_booking(user=user, stock=stock, venue=venue, is_cancelled=True)
            create_deposit(user, amount=50)
            repository.save(user, stock)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201

        @clean_database
        def when_user_cannot_book_free_offers_but_has_enough_credit_for_paid_offer(self, app):
            # Given
            user = create_user(can_book_free_offers=False)
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
            recommendation = create_recommendation(thing_offer, user)
            create_deposit(user)
            repository.save(user, stock)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201
            assert response.json['amount'] == 10.0
            assert response.json['quantity'] == 1

        @clean_database
        def when_already_booked_by_user_but_cancelled(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer)
            create_booking(user=user, stock=stock, venue=venue, is_cancelled=True)
            create_deposit(user)
            repository.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert response.status_code == 201

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
