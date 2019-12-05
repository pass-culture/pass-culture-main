from datetime import datetime, timedelta
from unittest.mock import patch

from models import Offerer, PcObject, EventType, ThingType
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_deposit, create_stock_with_event_offer, create_venue, create_offerer, \
    create_recommendation, create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_mediation
from utils.human_ids import humanize


class Post:
    class Returns400:
        @clean_database
        def when_non_validated_venue(self, app):
            # Given
            user = create_user(email='test@email.com')
            deposit = create_deposit(user)
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
            PcObject.save(stock, user, deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            r_create = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/bookings', json=booking_json)

            # Then
            assert r_create.status_code == 400
            assert r_create.json['stockId'] == [
                'Vous ne pouvez pas encore réserver cette offre, son lieu est en attente de validation']

        @clean_database
        def when_booking_limit_datetime_has_passed(self, app):
            # given
            offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')

            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')

            thing_offer = create_offer_with_thing_product(venue)

            expired_stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=0)
            expired_stock.bookingLimitDatetime = datetime.utcnow() - timedelta(seconds=1)
            PcObject.save(expired_stock)

            user = create_user(email='test@mail.com')
            PcObject.save(user)

            recommendation = create_recommendation(thing_offer, user)

            booking_json = {
                'stockId': humanize(expired_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            r_create = TestClient(app.test_client()) \
                .with_auth('test@mail.com') \
                .post('/bookings', json=booking_json)

            # then
            assert r_create.status_code == 400
            assert 'global' in r_create.json
            assert 'date limite' in r_create.json['global'][0]

        @clean_database
        def when_too_many_bookings(self, app):
            # given
            offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')
            too_many_bookings_stock = create_stock_with_thing_offer(offerer=Offerer(), venue=venue, offer=None,
                                                                    available=2)

            user = create_user(email='test@email.com')
            user2 = create_user(email='test2@email.com')

            deposit = create_deposit(user, amount=500)
            deposit2 = create_deposit(user2, amount=500)

            recommendation = create_recommendation(offer=too_many_bookings_stock.offer, user=user)

            booking = create_booking(user2, too_many_bookings_stock, venue, quantity=2)

            PcObject.save(booking, recommendation, user, deposit, deposit2, too_many_bookings_stock)

            booking_json = {
                'stockId': humanize(too_many_bookings_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            r_create = TestClient(app.test_client()) \
                .with_auth('test@email.com') \
                .post('/bookings', json=booking_json)

            # then
            assert r_create.status_code == 400
            assert 'global' in r_create.json
            assert 'quantité disponible' in r_create.json['global'][0]

        @clean_database
        def when_user_cannot_book_free_offers_and_free_offer(self, app):
            # Given
            user = create_user(email='cannotBook_freeOffers@email.com', can_book_free_offers=False)
            PcObject.save(user)

            offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                                     name='Test offerer')
            PcObject.save(offerer)

            venue = create_venue(offerer=offerer, name='Venue name', booking_email='booking@email.com',
                                 address='1 Test address', postal_code='93000', city='Test city', departement_code='93')
            PcObject.save(venue)

            thing_offer = create_offer_with_thing_product(venue)
            PcObject.save(thing_offer)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=0)
            PcObject.save(stock)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.save(recommendation)

            deposit = create_deposit(user, amount=500)
            PcObject.save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            r_create = TestClient(app.test_client()) \
                .with_auth('cannotBook_freeOffers@email.com') \
                .post('/bookings', json=booking_json)

            # Then
            assert r_create.status_code == 400
            assert 'cannotBookFreeOffers' in r_create.json
            assert r_create.json['cannotBookFreeOffers'] == [
                "Votre compte ne vous permet pas de faire de réservation."]

        @clean_database
        def when_user_has_not_enough_credit(self, app):
            # Given
            user = create_user(email='insufficient_funds_test@email.com')
            offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                                     name='Test offerer')
            venue = create_venue(offerer=offerer, name='Venue name', booking_email='booking@email.com',
                                 address='1 Test address', postal_code='93000', city='Test city', departement_code='93')
            stock = create_stock_with_event_offer(offerer, venue, price=200)
            event_offer = stock.resolvedOffer
            recommendation = create_recommendation(event_offer, user)
            deposit = create_deposit(user, amount=0)

            PcObject.save(recommendation)
            PcObject.save(stock)
            PcObject.save(deposit)

            booking_json = {
                "stockId": humanize(stock.id),
                "recommendationId": humanize(recommendation.id),
                "quantity": 1
            }

            # When
            r_create = TestClient(app.test_client()) \
                .with_auth('insufficient_funds_test@email.com') \
                .post('/bookings', json=booking_json)

            # Then
            assert r_create.status_code == 400
            assert 'insufficientFunds' in r_create.json
            assert r_create.json['insufficientFunds'] == [
                "Le solde de votre pass est insuffisant pour réserver cette offre."]

        @clean_database
        def when_only_public_credit_and_limit_of_physical_thing_reached(self, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.save(user)

            offerer = create_offerer()
            PcObject.save(offerer)

            venue = create_venue(offerer)
            PcObject.save(venue)

            thing_offer = create_offer_with_thing_product(venue)
            PcObject.save(thing_offer)

            thing_stock_price_190 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=190)

            thing_stock_price_12 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=12)

            PcObject.save(thing_stock_price_190, thing_stock_price_12)

            deposit = create_deposit(user, amount=500, source='public')

            PcObject.save(deposit)

            booking_thing_price_190 = create_booking(user, thing_stock_price_190, venue, recommendation=None)
            PcObject.save(booking_thing_price_190)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.save(recommendation)

            booking_thing_price_12_json = {
                "stockId": humanize(thing_stock_price_12.id),
                "recommendationId": humanize(recommendation.id),
                "quantity": 1
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth('test@email.com') \
                .post('/bookings', json=booking_thing_price_12_json)

            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['global'] == ['Le plafond de 200 € pour les biens culturels ' \
                                               'ne vous permet pas de réserver cette offre.']

        @clean_database
        def when_missing_stock_id(self, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.save(user)

            booking_json = {
                'stockId': None,
                'recommendationId': 'AFQA',
                'quantity': 2
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth('test@email.com') \
                .post('/bookings', json=booking_json)

            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['stockId'] == ['Vous devez préciser un identifiant d\'offre']

        @clean_database
        def when_missing_quantity(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            PcObject.save(user, stock)
            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': 'AFQA',
                'quantity': None
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['quantity'] == ['Vous devez préciser une quantité pour la réservation']

        @clean_database
        def when_negative_quantity(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': -3
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['quantity'] == ['Vous devez préciser une quantité pour la réservation']

        @clean_database
        def when_offer_is_inactive(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            thing_offer.isActive = False
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['stockId'] == ["Cette offre a été retirée. Elle n'est plus valable."]

        @clean_database
        def when_offerer_is_inactive(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            offerer.isActive = False
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['stockId'] == ["Cette offre a été retirée. Elle n'est plus valable."]

        @clean_database
        def when_stock_is_soft_deleted(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            stock.isSoftDeleted = True
            PcObject.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['stockId'] == ["Cette date a été retirée. Elle n'est plus disponible."]

        @clean_database
        def when_null_quantity(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 0
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['quantity'] == ['Vous devez préciser une quantité pour la réservation']

        @clean_database
        def when_quantity_is_more_than_one_and_offer_is_not_duo(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 5,
                'isDuo': False,
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['quantity'] == ["Vous ne pouvez pas réserver plus d'une offre à la fois"]

        @clean_database
        def when_quantity_is_more_than_two_and_offer_is_duo(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 3,
                'isDuo': True,
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['quantity'] == [
                "Vous ne pouvez pas réserver plus de deux places s'il s'agit d'une offre DUO"]

        @clean_database
        def when_event_occurrence_beginning_datetime_has_passed(self, app):
            # Given
            four_days_ago = datetime.utcnow() - timedelta(days=4)
            five_days_ago = datetime.utcnow() - timedelta(days=5)
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            deposit = create_deposit(user, amount=200)
            offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=five_days_ago,
                                                       end_datetime=four_days_ago)
            stock = create_stock_from_event_occurrence(event_occurrence, price=20)

            PcObject.save(deposit, stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)

            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['date'] == ["Cette offre n'est plus valable car sa date est passée"]

        @clean_database
        def when_thing_booking_limit_datetime_has_expired(self, app):
            # Given
            four_days_ago = datetime.utcnow() - timedelta(days=4)
            five_days_ago = datetime.utcnow() - timedelta(days=5)
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            deposit = create_deposit(user, amount=200)
            venue = create_venue(offerer)

            stock = create_stock_with_thing_offer(offerer, venue, price=20, booking_limit_datetime=four_days_ago)

            PcObject.save(deposit, stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)

            # Then
            error_message = response.json
            assert response.status_code == 400
            assert error_message['global'] == ["La date limite de réservation de cette offre est dépassée"]

        @clean_database
        def when_already_booked_by_user(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            create_deposit(user, amount=200)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            booking = create_booking(user, stock, venue, is_cancelled=False)
            PcObject.save(stock, user, booking)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)

            # Then
            assert response.status_code == 400
            error_message = response.json
            assert error_message['stockId'] == ["Cette offre a déja été reservée par l'utilisateur"]

    class Returns201:
        @clean_database
        @patch('routes.bookings.send_raw_email')
        def expect_the_booking_to_have_good_includes(self, send_raw_email_mock, app):
            offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')
            ok_stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0)
            ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
            PcObject.save(ok_stock)
            mediation = create_mediation(ok_stock.offer)
            PcObject.save(mediation)

            user = create_user(email='test@mail.com')
            PcObject.save(user)

            recommendation = create_recommendation(offer=ok_stock.offer, user=user)
            PcObject.save(recommendation)

            booking_json = {
                'stockId': humanize(ok_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            r_create = TestClient(app.test_client()).with_auth(email='test@mail.com').post('/bookings',
                                                                                           json=booking_json)
            assert r_create.status_code == 201
            assert r_create.json['stock']['isBookable']

        @clean_database
        @patch('routes.bookings.send_raw_email')
        def when_limit_date_is_in_the_future_and_offer_is_free(self, send_raw_email_mock, app):
            offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')
            ok_stock = create_stock_with_event_offer(offerer=offerer, venue=venue, price=0)
            ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
            ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
            PcObject.save(ok_stock)
            mediation = create_mediation(ok_stock.offer)
            PcObject.save(mediation)

            user = create_user(email='test@mail.com')
            PcObject.save(user)

            recommendation = create_recommendation(offer=ok_stock.offer, user=user)
            PcObject.save(recommendation)

            booking_json = {
                'stockId': humanize(ok_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            r_create = TestClient(app.test_client()).with_auth(email='test@mail.com').post('/bookings',
                                                                                           json=booking_json)
            assert r_create.status_code == 201
            id = r_create.json['id']
            r_check = TestClient(app.test_client()).with_auth(email='test@mail.com').get(
                '/bookings/' + id)
            created_booking_json = r_check.json
            for (key, value) in booking_json.items():
                assert created_booking_json[key] == booking_json[key]

        @clean_database
        @patch('routes.bookings.send_raw_email')
        def when_booking_limit_datetime_is_none(self, send_raw_email_mock, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            deposit = create_deposit(user, amount=200)
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=20, booking_limit_datetime=None)

            PcObject.save(deposit, stock, user)
            mediation = create_mediation(thing_offer)
            PcObject.save(mediation)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            assert response.status_code == 201

        @clean_database
        @patch('routes.bookings.send_raw_email')
        def when_user_has_enough_credit(self, send_raw_email_mock, app):
            # Given
            offerer = create_offerer('819202819', '1 Fake Address', 'Fake city', '93000', 'Fake offerer')
            venue = create_venue(offerer, 'venue name', 'booking@email.com', '1 fake street', '93000', 'False city',
                                 '93')
            thing_offer = create_offer_with_thing_product(venue)

            user = create_user(email='test@email.com')
            PcObject.save(user)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=50, available=1)
            PcObject.save(stock)
            mediation = create_mediation(thing_offer)
            PcObject.save(mediation)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.save(recommendation)

            deposit = create_deposit(user, amount=50)
            PcObject.save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth('test@email.com') \
                .post('/bookings', json=booking_json)

            # then
            assert response.status_code == 201
            assert 'recommendation' in response.json
            assert 'offer' in response.json['recommendation']
            assert 'venue' in response.json['recommendation']['offer']
            assert 'validationToken' not in response.json['recommendation']['offer']['venue']

        @clean_database
        @patch('routes.bookings.send_raw_email')
        def when_user_respects_expenses_limits(self, send_raw_email_mock, app):
            # Given
            offerer = create_offerer('819202819', '1 Fake Address', 'Fake city', '93000', 'Fake offerer')
            venue = create_venue(offerer, 'venue name', 'booking@email.com', '1 fake street', '93000', 'False city',
                                 '93')
            thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO_ABO)

            user = create_user(email='test@email.com')
            PcObject.save(user)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=210, available=1)
            PcObject.save(stock)

            mediation = create_mediation(thing_offer)
            PcObject.save(mediation)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.save(recommendation)

            deposit = create_deposit(user, amount=500)
            PcObject.save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth('test@email.com') \
                .post('/bookings', json=booking_json)

            # then
            assert response.status_code == 201

        @clean_database
        @patch('routes.bookings.send_raw_email')
        def when_user_has_enough_credit_after_cancelling_booking(self, send_raw_email_mock, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.save(user)

            deposit = create_deposit(user, amount=50)
            PcObject.save(deposit)

            offerer = create_offerer('819202819', '1 Fake Address', 'Fake city', '93000', 'Fake offerer')
            venue = create_venue(offerer, 'venue name', 'booking@email.com', '1 fake street', '93000', 'False city',
                                 '93')

            stock = create_stock_with_event_offer(offerer, venue, price=50, available=1)
            PcObject.save(stock)
            mediation = create_mediation(stock.offer)
            PcObject.save(mediation)

            booking = create_booking(user, stock, venue, is_cancelled=True)
            PcObject.save(booking)

            recommendation = create_recommendation(stock.offer, user)
            PcObject.save(recommendation)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            r_create = TestClient(app.test_client()) \
                .with_auth('test@email.com') \
                .post('/bookings', json=booking_json)

            # then
            assert r_create.status_code == 201

        @clean_database
        @patch('routes.bookings.send_raw_email')
        def when_user_cannot_book_free_offers_but_has_enough_credit_for_paid_offer(self, send_raw_email_mock, app):
            user = create_user(email='can_book_paid_offers@email.com', can_book_free_offers=False)
            PcObject.save(user)

            offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                                     name='Test offerer')
            PcObject.save(offerer)

            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')
            PcObject.save(venue)

            thing_offer = create_offer_with_thing_product(venue)
            PcObject.save(thing_offer)

            mediation = create_mediation(thing_offer)
            PcObject.save(mediation)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
            PcObject.save(stock)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.save(recommendation)

            deposit = create_deposit(user, amount=500)
            PcObject.save(deposit)

            booking_json = {
                "stockId": humanize(stock.id),
                "recommendationId": humanize(recommendation.id),
                "quantity": 1
            }

            # When
            r_create = TestClient(app.test_client()) \
                .with_auth('can_book_paid_offers@email.com') \
                .post('/bookings', json=booking_json)

            # Then
            r_create_json = r_create.json
            assert r_create.status_code == 201
            assert r_create_json['amount'] == 10.0
            assert r_create_json['quantity'] == 1

        @clean_database
        @patch('routes.bookings.send_raw_email')
        def when_already_booked_by_user_but_cancelled(self, send_raw_email_mock, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue)
            mediation = create_mediation(thing_offer)
            create_deposit(user, amount=200)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            booking = create_booking(user, stock, venue, is_cancelled=True)
            PcObject.save(mediation)
            PcObject.save(stock, user, booking)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient(app.test_client()).with_auth('test@email.com').post('/bookings',
                                                                                      json=booking_json)
            # Then
            assert response.status_code == 201
