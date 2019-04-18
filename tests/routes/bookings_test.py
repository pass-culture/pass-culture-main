import pytest
from datetime import datetime, timedelta
from urllib.parse import urlencode

from models import Offerer, PcObject, EventType, ThingType, Deposit
from models.db import db
from models.pc_object import serialize
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_stock_with_thing_offer, \
    create_thing_offer, create_deposit, create_stock_with_event_offer, create_venue, create_offerer, \
    create_recommendation, create_user, create_booking, create_event_offer, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer
from utils.human_ids import humanize


@pytest.mark.standalone
class Post:
    class Returns400:
        @clean_database
        def when_non_validated_venue(self, app):
            # Given
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, datetime.utcnow())
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            thing_offer = create_thing_offer(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
            PcObject.check_and_save(stock, user, deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            r_create = TestClient() \
                .with_auth(user.email) \
                .post(API_URL + '/bookings', json=booking_json)

            # Then
            assert r_create.status_code == 400
            assert r_create.json()['stockId'] == [
                'Vous ne pouvez pas encore réserver cette offre, son lieu est en attente de validation']

        @clean_database
        def when_booking_limit_datetime_has_passed(self, app):
            # given
            offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')

            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')

            thing_offer = create_thing_offer(venue)

            expired_stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, thing_offer=thing_offer,
                                                          price=0)
            expired_stock.bookingLimitDatetime = datetime.utcnow() - timedelta(seconds=1)
            PcObject.check_and_save(expired_stock)

            user = create_user(email='test@mail.com')
            PcObject.check_and_save(user)

            recommendation = create_recommendation(thing_offer, user)

            booking_json = {
                'stockId': humanize(expired_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            r_create = TestClient() \
                .with_auth('test@mail.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # then
            assert r_create.status_code == 400
            assert 'global' in r_create.json()
            assert 'date limite' in r_create.json()['global'][0]

        @clean_database
        def when_too_many_bookings(self, app):
            # given
            offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')
            too_many_bookings_stock = create_stock_with_thing_offer(offerer=Offerer(), venue=venue, thing_offer=None,
                                                                    available=2)

            user = create_user(email='test@email.com')
            user2 = create_user(email='test2@email.com')

            deposit = create_deposit(user, datetime.utcnow(), amount=500)
            deposit2 = create_deposit(user2, datetime.utcnow(), amount=500)

            recommendation = create_recommendation(offer=too_many_bookings_stock.offer, user=user)

            booking = create_booking(user2, too_many_bookings_stock, venue, quantity=2)

            PcObject.check_and_save(booking, recommendation, user, deposit, deposit2, too_many_bookings_stock)

            booking_json = {
                'stockId': humanize(too_many_bookings_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            r_create = TestClient() \
                .with_auth('test@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # then
            assert r_create.status_code == 400
            assert 'global' in r_create.json()
            assert 'quantité disponible' in r_create.json()['global'][0]

        @clean_database
        def when_user_cannot_book_free_offers_and_free_offer(self, app):
            # Given
            user = create_user(email='cannotBook_freeOffers@email.com', can_book_free_offers=False)
            PcObject.check_and_save(user)

            offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                                     name='Test offerer')
            PcObject.check_and_save(offerer)

            venue = create_venue(offerer=offerer, name='Venue name', booking_email='booking@email.com',
                                 address='1 Test address', postal_code='93000', city='Test city', departement_code='93')
            PcObject.check_and_save(venue)

            thing_offer = create_thing_offer(venue)
            PcObject.check_and_save(thing_offer)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=0)
            PcObject.check_and_save(stock)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.check_and_save(recommendation)

            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=500)
            PcObject.check_and_save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # When
            r_create = TestClient() \
                .with_auth('cannotBook_freeOffers@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # Then
            assert r_create.status_code == 400
            assert 'cannotBookFreeOffers' in r_create.json()
            assert r_create.json()['cannotBookFreeOffers'] == [
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
            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=0)

            PcObject.check_and_save(recommendation)
            PcObject.check_and_save(stock)
            PcObject.check_and_save(deposit)

            booking_json = {
                "stockId": humanize(stock.id),
                "recommendationId": humanize(recommendation.id),
                "quantity": 1
            }

            # When
            r_create = TestClient() \
                .with_auth('insufficient_funds_test@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # Then
            assert r_create.status_code == 400
            assert 'insufficientFunds' in r_create.json()
            assert r_create.json()['insufficientFunds'] == [
                "Le solde de votre pass n'est pas suffisant pour effectuer cette réservation."]

        @clean_database
        def when_only_public_credit_and_limit_of_physical_thing_reached(self, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.check_and_save(user)

            offerer = create_offerer()
            PcObject.check_and_save(offerer)

            venue = create_venue(offerer)
            PcObject.check_and_save(venue)

            thing_offer = create_thing_offer(venue)
            PcObject.check_and_save(thing_offer)

            thing_stock_price_190 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=190)

            thing_stock_price_12 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=12)

            PcObject.check_and_save(thing_stock_price_190, thing_stock_price_12)

            deposit_date = datetime.utcnow() - timedelta(minutes=2)

            deposit = create_deposit(user, deposit_date, amount=500, source='public')

            PcObject.check_and_save(deposit)

            booking_thing_price_190 = create_booking(user, thing_stock_price_190, venue, recommendation=None)
            PcObject.check_and_save(booking_thing_price_190)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.check_and_save(recommendation)

            booking_thing_price_12_json = {
                "stockId": humanize(thing_stock_price_12.id),
                "recommendationId": humanize(recommendation.id),
                "quantity": 1
            }

            # When
            response = TestClient() \
                .with_auth('test@email.com') \
                .post(API_URL + '/bookings', json=booking_thing_price_12_json)

            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['global'] == ['La limite de 200 € pour les biens culturels ' \
                                               'ne vous permet pas de réserver']

        @clean_database
        def when_missing_stock_id(self, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.check_and_save(user)

            booking_json = {
                'stockId': None,
                'recommendationId': 'AFQA',
                'quantity': 2
            }

            # When
            response = TestClient() \
                .with_auth('test@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['stockId'] == ['Vous devez préciser un identifiant d\'offre']

        @clean_database
        def when_missing_quantity(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            PcObject.check_and_save(user, stock)
            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': 'AFQA',
                'quantity': None
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['quantity'] == ['Vous devez préciser une quantité pour la réservation']

        @clean_database
        def when_negative_quantity(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.check_and_save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': -3
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['quantity'] == ['Vous devez préciser une quantité pour la réservation']

        @clean_database
        def when_offer_is_inactive(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            thing_offer.isActive = False
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.check_and_save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['stockId'] == ["Cette offre a été retirée. Elle n'est plus valable."]

        @clean_database
        def when_offerer_is_inactive(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            offerer.isActive = False
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.check_and_save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['stockId'] == ["Cette offre a été retirée. Elle n'est plus valable."]

        @clean_database
        def when_stock_is_soft_deleted(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            stock.isSoftDeleted = True
            PcObject.check_and_save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1,
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['stockId'] == ["Cette date a été retirée. Elle n'est plus disponible."]

        @clean_database
        def when_null_quantity(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.check_and_save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 0
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['quantity'] == ['Vous devez préciser une quantité pour la réservation']

        @clean_database
        def when_more_than_one_quantity(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            PcObject.check_and_save(stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 5
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['quantity'] == ["Vous ne pouvez pas réserver plus d'une offre à la fois"]

        @clean_database
        def when_event_occurrence_beginning_datetime_has_passed(self, app):
            # Given
            four_days_ago = datetime.utcnow() - timedelta(days=4)
            five_days_ago = datetime.utcnow() - timedelta(days=5)
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=200)
            offer = create_event_offer(venue, event_name='Event Name', event_type=EventType.CINEMA)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=five_days_ago,
                                                       end_datetime=four_days_ago)
            stock = create_stock_from_event_occurrence(event_occurrence, price=20)

            PcObject.check_and_save(deposit, stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)

            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['date'] == ["Cette offre n'est plus valable car sa date est passée"]

        @clean_database
        def when_thing_booking_limit_datetime_has_expired(self, app):
            # Given
            four_days_ago = datetime.utcnow() - timedelta(days=4)
            five_days_ago = datetime.utcnow() - timedelta(days=5)
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=200)
            venue = create_venue(offerer)

            stock = create_stock_with_thing_offer(offerer, venue, price=20, booking_limit_datetime=four_days_ago)

            PcObject.check_and_save(deposit, stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)

            # Then
            error_message = response.json()
            assert response.status_code == 400
            assert error_message['global'] == ["La date limite de réservation de cette offre est dépassée"]

        @clean_database
        def when_already_booked_by_user(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=200)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            booking = create_booking(user, stock, venue, is_cancelled=False)
            PcObject.check_and_save(stock, user, booking)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)

            # Then
            assert response.status_code == 400
            error_message = response.json()
            assert error_message['stockId'] == ["Cette offre a déja été reservée par l'utilisateur"]

    class Returns201:
        @clean_database
        def when_limit_date_is_in_the_future_and_offer_is_free(self, app):
            offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')
            ok_stock = create_stock_with_event_offer(offerer=offerer,
                                                     venue=venue, price=0)
            ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
            ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
            PcObject.check_and_save(ok_stock)

            user = create_user(email='test@mail.com')
            PcObject.check_and_save(user)

            recommendation = create_recommendation(offer=ok_stock.offer, user=user)
            PcObject.check_and_save(recommendation)

            booking_json = {
                'stockId': humanize(ok_stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            r_create = TestClient().with_auth(email='test@mail.com').post(API_URL + '/bookings',
                                                                          json=booking_json)
            assert r_create.status_code == 201
            id = r_create.json()['id']
            r_check = TestClient().with_auth(email='test@mail.com').get(
                API_URL + '/bookings/' + id)
            created_booking_json = r_check.json()
            for (key, value) in booking_json.items():
                assert created_booking_json[key] == booking_json[key]

        @clean_database
        def when_booking_limit_datetime_is_None(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=200)
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=20, booking_limit_datetime=None)

            PcObject.check_and_save(deposit, stock, user)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            error_message = response.json()
            assert response.status_code == 201

        @clean_database
        def when_user_has_enough_credit(self, app):
            # Given
            offerer = create_offerer('819202819', '1 Fake Address', 'Fake city', '93000', 'Fake offerer')
            venue = create_venue(offerer, 'venue name', 'booking@email.com', '1 fake street', '93000', 'False city',
                                 '93')
            thing_offer = create_thing_offer(venue)

            user = create_user(email='test@email.com')
            PcObject.check_and_save(user)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=50, available=1)
            PcObject.check_and_save(stock)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.check_and_save(recommendation)

            deposit = create_deposit(user, datetime.utcnow(), amount=50)
            PcObject.check_and_save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            response = TestClient() \
                .with_auth('test@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # then
            assert response.status_code == 201

        @clean_database
        def when_user_respects_expenses_limits(self, app):
            # Given
            offerer = create_offerer('819202819', '1 Fake Address', 'Fake city', '93000', 'Fake offerer')
            venue = create_venue(offerer, 'venue name', 'booking@email.com', '1 fake street', '93000', 'False city',
                                 '93')
            thing_offer = create_thing_offer(venue, thing_type=ThingType.JEUX_ABO)

            user = create_user(email='test@email.com')
            PcObject.check_and_save(user)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=210, available=1)
            PcObject.check_and_save(stock)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.check_and_save(recommendation)

            deposit = create_deposit(user, datetime.utcnow(), amount=500)
            PcObject.check_and_save(deposit)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            response = TestClient() \
                .with_auth('test@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # then
            assert response.status_code == 201

        @clean_database
        def when_user_has_enough_credit_after_cancelling_booking(self, app):
            # Given
            user = create_user(email='test@email.com')
            PcObject.check_and_save(user)

            deposit = create_deposit(user, datetime.utcnow(), amount=50)
            PcObject.check_and_save(deposit)

            offerer = create_offerer('819202819', '1 Fake Address', 'Fake city', '93000', 'Fake offerer')
            venue = create_venue(offerer, 'venue name', 'booking@email.com', '1 fake street', '93000', 'False city',
                                 '93')
            event_offer = create_event_offer(venue)

            stock = create_stock_with_event_offer(offerer, venue, event_offer, price=50, available=1)
            PcObject.check_and_save(stock)

            booking = create_booking(user, stock, venue, is_cancelled=True)
            PcObject.check_and_save(booking)

            recommendation = create_recommendation(event_offer, user)
            PcObject.check_and_save(recommendation)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': humanize(recommendation.id),
                'quantity': 1
            }

            # when
            r_create = TestClient() \
                .with_auth('test@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # then
            assert r_create.status_code == 201

        @clean_database
        def when_user_cannot_book_free_offers_but_has_enough_credit_for_paid_offer(self, app):
            user = create_user(email='can_book_paid_offers@email.com', can_book_free_offers=False)
            PcObject.check_and_save(user)

            offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                                     name='Test offerer')
            PcObject.check_and_save(offerer)

            venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                                 '93')
            PcObject.check_and_save(venue)

            thing_offer = create_thing_offer(venue)
            PcObject.check_and_save(thing_offer)

            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
            PcObject.check_and_save(stock)

            recommendation = create_recommendation(thing_offer, user)
            PcObject.check_and_save(recommendation)

            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=500)
            PcObject.check_and_save(deposit)

            booking_json = {
                "stockId": humanize(stock.id),
                "recommendationId": humanize(recommendation.id),
                "quantity": 1
            }

            # When
            r_create = TestClient() \
                .with_auth('can_book_paid_offers@email.com') \
                .post(API_URL + '/bookings', json=booking_json)

            # Then
            r_create_json = r_create.json()
            assert r_create.status_code == 201
            assert r_create_json['amount'] == 10.0
            assert r_create_json['quantity'] == 1

        @clean_database
        def when_already_booked_by_user_but_cancelled(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            thing_offer = create_thing_offer(venue)
            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=200)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
            booking = create_booking(user, stock, venue, is_cancelled=True)
            PcObject.check_and_save(stock, user, booking)

            booking_json = {
                'stockId': humanize(stock.id),
                'recommendationId': None,
                'quantity': 1
            }

            # When
            response = TestClient().with_auth('test@email.com').post(API_URL + '/bookings',
                                                                     json=booking_json)
            # Then
            assert response.status_code == 201


@pytest.mark.standalone
class PatchBookingTest:
    @clean_database
    def test_cannot_cancel_used_booking(self, app):
        # Given
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        booking = create_booking(user, is_used=True)
        PcObject.check_and_save(user, deposit, booking)
        url = API_URL + '/bookings/' + humanize(booking.id)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 400
        assert response.json()['booking'] == ["Impossible d\'annuler une réservation consommée"]
        db.session.refresh(booking)
        assert not booking.isCancelled

    @clean_database
    def test_returns_400_when_trying_to_patch_something_else_than_is_cancelled(self, app):
        # Given
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        booking = create_booking(user, quantity=1)
        PcObject.check_and_save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"quantity": 3})

        # Then
        assert response.status_code == 400
        db.session.refresh(booking)
        assert booking.quantity == 1

    @clean_database
    def test_returns_400_when_trying_to_set_is_cancelled_to_false(self, app):
        # Given
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        booking = create_booking(user)
        booking.isCancelled = True
        PcObject.check_and_save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": False})

        # Then
        assert response.status_code == 400
        db.session.refresh(booking)
        assert booking.isCancelled

    @clean_database
    def test_returns_200_and_effectively_marks_the_booking_as_cancelled_when_valid_usecase(self, app):
        # Given
        in_four_days = datetime.utcnow() + timedelta(days=4)
        in_five_days = datetime.utcnow() + timedelta(days=5)
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=in_four_days, end_datetime=in_five_days)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user, stock, venue)
        PcObject.check_and_save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 200
        db.session.refresh(booking)
        assert booking.isCancelled

    @clean_database
    def test_returns_404_if_booking_does_not_exist(self, app):
        # Given
        user = create_user(email='test@email.com')
        PcObject.check_and_save(user)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/AX', json={"isCancelled": True})

        # Then
        assert response.status_code == 404

    @clean_database
    def test_returns_403_and_does_not_mark_the_booking_as_cancelled_when_cancelling_for_other_user(self, app):
        # Given
        other_user = create_user(email='test2@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(other_user, deposit_date, amount=500)
        booking = create_booking(other_user)
        user = create_user(email='test@email.com')
        PcObject.check_and_save(user, other_user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 403
        db.session.refresh(booking)
        assert not booking.isCancelled

    @clean_database
    def test_returns_200_and_effectively_marks_the_booking_as_cancelled_when_cancelling_for_other_as_admin(self, app):
        # Given
        admin_user = create_user(email='test@email.com', can_book_free_offers=False, is_admin=True)
        other_user = create_user(email='test2@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(other_user, deposit_date, amount=500)
        booking = create_booking(other_user)
        PcObject.check_and_save(admin_user, other_user, deposit, booking)

        # When
        response = TestClient().with_auth(admin_user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 200
        db.session.refresh(booking)
        assert booking.isCancelled


@pytest.mark.standalone
class GetBookingByTokenTest:
    @clean_database
    def test_when_user_has_rights_and_regular_offer_returns_status_code_200_user_and_booking_data(self, app):
        # Given
        user = create_user(public_name='John Doe', email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name', event_type=EventType.CINEMA)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(user_offerer, booking)

        expected_json = {'bookingId': humanize(booking.id),
                         'date': serialize(booking.stock.beginningDatetime),
                         'email': 'user@email.fr',
                         'isUsed': False,
                         'offerName': 'Event Name',
                         'userName': 'John Doe',
                         'venueDepartementCode': '93'}

        # When
        response = TestClient().with_auth('admin@email.fr').get(
            API_URL + '/bookings/token/{}'.format(booking.token))
        # Then
        assert response.status_code == 200
        response_json = response.json()
        assert response_json == expected_json

    @clean_database
    def test_when_activation_event_and_user_has_rights_returns_user_and_booking_data_with_phone_number_and_date_of_birth(
            self, app):
        # Given
        user = create_user(email='user@email.fr', phone_number='0698765432', date_of_birth=datetime(2001, 2, 1))
        admin_user = create_user(email='admin@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Offre d\'activation', event_type=EventType.ACTIVATION)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(admin_user, booking)

        expected_json = {'bookingId': humanize(booking.id),
                         'date': serialize(booking.stock.beginningDatetime),
                         'dateOfBirth': '2001-02-01T00:00:00Z',
                         'email': 'user@email.fr',
                         'isUsed': False,
                         'offerName': 'Offre d\'activation',
                         'phoneNumber': '0698765432',
                         'userName': 'John Doe',
                         'venueDepartementCode': '93'}

        # When
        response = TestClient() \
            .with_auth('admin@email.fr') \
            .get(API_URL + '/bookings/token/{}'.format(booking.token))

        # Then
        assert response.status_code == 200
        response_json = response.json()
        assert response_json == expected_json

    @clean_database
    def test_when_user_has_rights_and_email_with_special_characters_url_encoded_returns_status_code_200(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        user_admin = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(user_offerer, booking)
        url_email = urlencode({'email': 'user+plus@email.fr'})
        url = API_URL + '/bookings/token/{}?{}'.format(booking.token, url_email)

        # When
        response = TestClient().with_auth('admin@email.fr').get(url)
        # Then
        assert response.status_code == 200

    @clean_database
    def test_when_user_doesnt_have_rights_returns_status_code_204(self, app):
        # Given
        user = create_user(email='user@email.fr')
        querying_user = create_user(email='querying@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(querying_user, booking)

        # When
        response = TestClient().with_auth('querying@email.fr').get(
            API_URL + '/bookings/token/{}'.format(booking.token))
        # Then
        assert response.status_code == 204

    @clean_database
    def test_when_user_not_logged_in_and_gives_right_email_returns_204(self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(admin_user, booking)

        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, 'user@email.fr')
        # When
        response = TestClient().get(url)
        # Then
        assert response.status_code == 204

    @clean_database
    def test_when_user_not_logged_in_and_give_right_email_and_event_offer_id_returns_204(self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(admin_user, booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                         humanize(offer.id))

        # When
        response = TestClient().get(url)

        # Then
        assert response.status_code == 204

    @clean_database
    def test_when_not_logged_in_and_give_right_email_and_offer_id_thing_returns_204(self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(admin_user, booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                         humanize(stock.offerId))

        # When
        response = TestClient().get(url)
        # Then
        assert response.status_code == 204

    @clean_database
    def test_when_token_user_has_rights_but_token_not_found_returns_status_code_404_and_global_error(self, app):
        # Given
        admin_user = create_user(email='admin@email.fr')
        PcObject.check_and_save(admin_user)

        # When
        response = TestClient().with_auth('admin@email.fr').get(
            API_URL + '/bookings/token/{}'.format('12345'))
        # Then
        assert response.status_code == 404
        assert response.json()['global'] == ["Cette contremarque n'a pas été trouvée"]

    @clean_database
    def test_when_user_not_logged_in_and_wrong_email_returns_404_and_global_in_error(self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(admin_user, booking)

        # When
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, 'toto@email.fr')
        response = TestClient().with_auth('admin@email.fr').get(url)
        # Then
        assert response.status_code == 404
        assert response.json()['global'] == ["Cette contremarque n'a pas été trouvée"]

    @clean_database
    def test_when_user_not_logged_in_right_email_and_wrong_offer_returns_404_and_global_in_error(self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(admin_user, booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr', humanize(123))

        # When
        response = TestClient().get(url)

        # Then
        assert response.status_code == 404
        assert response.json()['global'] == ["Cette contremarque n'a pas été trouvée"]

    @clean_database
    def test_when_user_has_rights_and_email_with_special_characters_not_url_encoded_returns_404(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        user_admin = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(user_offerer, booking)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

        # When
        response = TestClient().with_auth('admin@email.fr').get(url)
        # Then
        assert response.status_code == 404

    @clean_database
    def test_when_user_not_logged_in_and_doesnt_give_email_returns_400_and_email_in_error(self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(admin_user, booking)

        url = API_URL + '/bookings/token/{}'.format(booking.token)
        # When
        response = TestClient().get(url)
        # Then
        assert response.status_code == 400
        error_message = response.json()
        assert error_message['email'] == [
            'Vous devez préciser l\'email de l\'utilisateur quand vous n\'êtes pas connecté(e)']

    @clean_database
    def test_when_not_logged_in_give_right_email_and_offer_id_thing_but_already_validated_token_returns_410_and_booking_in_error(
            self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=0)
        booking = create_booking(user, stock, venue=venue, is_used=True)

        PcObject.check_and_save(admin_user, booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                         humanize(stock.offerId))

        # When
        response = TestClient().get(url)
        # Then
        assert response.status_code == 410
        assert response.json()['booking'] == ['Cette réservation a déjà été validée']

    @clean_database
    def test_when_not_logged_in_and_give_right_email_and_offer_id_thing_but_cancelled_booking_returns_410_and_booking_in_error(
            self, app):
        # Given
        user = create_user(email='user@email.fr')
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=0)
        booking = create_booking(user, stock, venue=venue, is_cancelled=True)

        PcObject.check_and_save(admin_user, booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                         humanize(stock.offerId))

        # When
        response = TestClient().get(url)
        # Then
        assert response.status_code == 410
        assert response.json()['booking'] == ['Cette réservation a été annulée']


@pytest.mark.standalone
class PatchBookingAsAnonymousUserTest:
    @clean_database
    def test_with_token_and_valid_email_and_offer_id_returns_204_and_sets_booking_is_used(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, user.email,
                                                                         humanize(stock.resolvedOffer.id))

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.isUsed is True

    @clean_database
    def test_patch_booking_with_token_and_offer_id_without_email_returns_400(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking)
        url = API_URL + '/bookings/token/{}?&offer_id={}'.format(booking.token, humanize(stock.resolvedOffer.id))

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 400
        assert response.json()['email'] == [
            "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"]

    @clean_database
    def test_patch_booking_with_token_and_email_without_offer_id_returns_400(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 400
        assert response.json()['offer_id'] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]

    @clean_database
    def test_patch_booking_with_token_without_offer_id_and_without_email_returns_400_with_both_errors(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking)
        url = API_URL + '/bookings/token/{}'.format(booking.token, user.email)

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 400
        assert response.json()['offer_id'] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]
        assert response.json()['email'] == [
            "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"]

    @clean_database
    def test_patch_booking_with_token_returns_404_if_booking_missing(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'wrong.email@test.com',
                                                                         humanize(stock.resolvedOffer.id))

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 404
        assert response.json()['global'] == ["Cette contremarque n'a pas été trouvée"]


@pytest.mark.standalone
class PatchBookingByTokenAsLoggedInUserTest:
    @clean_database
    def test_when_has_rights_returns_204_and_is_used_is_true(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.isUsed == True

    @clean_database
    def test_valid_request_with_non_standard_header_returns_204_and_is_used_is_true(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr', headers={'origin': 'http://random_header.fr'}).patch(url)

        # Then
        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.isUsed == True

    @clean_database
    def test_valid_request_and_email_with_special_character_url_encoded_returns_204(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        user_admin = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(user_offerer, booking)
        url_email = urlencode({'email': 'user+plus@email.fr'})
        url = API_URL + '/bookings/token/{}?{}'.format(booking.token, url_email)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)
        # Then
        assert response.status_code == 204

    @clean_database
    def test_when_user_not_editor_and_valid_email_returns_403_global_in_error_and_is_used_is_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, admin_user)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 403
        assert response.json()['global'] == ["Cette structure n'est pas enregistr\u00e9e chez cet utilisateur."]
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_when_user_not_editor_and_invalid_email_returns_404_and_is_used_is_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, admin_user)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, 'wrong@email.fr')

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 404
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_email_with_special_character_not_url_encoded_returns_404(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        user_admin = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.check_and_save(user_offerer, booking)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)
        # Then
        assert response.status_code == 404

    @clean_database
    def test_when_user_not_editor_and_valid_email_but_invalid_offer_id_returns_404_and_is_used_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, admin_user)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, user.email, humanize(123))

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 404
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_valid_request_when_booking_is_cancelled_returns_410_and_booking_in_error_and_is_used_is_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        booking.isCancelled = True
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 410
        assert response.json()['booking'] == ['Cette réservation a été annulée']
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_valid_request_when_booking_already_validated_returns_410_and_booking_in_error_and_is_used_is_false(self,
                                                                                                                app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        booking.isUsed = True
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 410
        assert response.json()['booking'] == ['Cette réservation a déjà été validée']
        db.session.refresh(booking)
        assert booking.isUsed == True


@pytest.mark.standalone
class GetBookingTest:
    @clean_database
    def test_get_booking_with_url_has_completed_url(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_thing_offer(venue, url='https://host/path/{token}?offerId={offerId}&email={email}')
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, thing_offer=offer, price=0)
        booking = create_booking(user, stock, venue=venue, token='ABCDEF')

        PcObject.check_and_save(booking)

        # When
        response = TestClient().with_auth(user.email).get(
            API_URL + '/bookings/' + humanize(booking.id))

        # Then
        assert response.status_code == 200
        response_json = response.json()
        assert response_json[
                   'completedUrl'] == 'https://host/path/ABCDEF?offerId=%s&email=user+plus@email.fr' % humanize(
            offer.id)

@pytest.mark.standalone
class GetBookingsCsvTest:
    @clean_database
    def test_get_bookings_csv(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        deposit = create_deposit(user, datetime.utcnow(), amount=500, source='public')
        offerer1 = create_offerer()
        offerer2 = create_offerer(siren='123456788')
        user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
        user_offerer2 = create_user_offerer(user, offerer2, validation_token=None)
        venue1 = create_venue(offerer1)
        venue2 = create_venue(offerer1, siret='12345678912346')
        venue3 = create_venue(offerer2, siret='12345678912347')
        offer1 = create_thing_offer(venue1, url='https://host/path/{token}?offerId={offerId}&email={email}')
        offer2 = create_thing_offer(venue2)
        offer3 = create_thing_offer(venue3)
        offer4 = create_thing_offer(venue3)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, thing_offer=offer1, price=10)
        stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, thing_offer=offer2, price=11)
        stock3 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, thing_offer=offer3, price=12)
        stock4 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, thing_offer=offer4, price=13)
        booking1 = create_booking(user, stock1, venue=venue1, token='ABCDEF')
        booking2 = create_booking(user, stock1, venue=venue1, token='ABCDEG')
        booking3 = create_booking(user, stock2, venue=venue2, token='ABCDEH')
        booking4 = create_booking(user, stock3, venue=venue3, token='ABCDEI')
        booking5 = create_booking(user, stock4, venue=venue3, token='ABCDEJ')
        booking6 = create_booking(user, stock4, venue=venue3, token='ABCDEK')

        PcObject.check_and_save(deposit, booking1, booking2, booking3,
                                booking4, booking5, booking6, user_offerer1,
                                user_offerer2)

        # When
        response = TestClient().with_auth(user.email).get(
            API_URL + '/bookings/csv')
        response_lines = response.text.split('\n')

        # Then
        assert response.status_code == 200
        assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
        assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
        assert len(response_lines) == 8

    @clean_database
    def test_get_bookings_csv_no_user_offerer(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        PcObject.check_and_save(user)

        # When
        response = TestClient().with_auth(user.email).get(
            API_URL + '/bookings/csv')
        response_lines = response.text.split('\n')

        # Then
        assert response.status_code == 200
        assert len(response_lines) == 2


@pytest.mark.standalone
class PatchBookingByTokenForActivationOffersTest:
    @clean_database
    def test_when_user_patching_admin_and_activation_event_returns_status_code_204_set_can_book_free_offers_true_for_booking_user(
            self, app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_event_offer(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        db.session.refresh(user)
        assert response.status_code == 204
        assert user.canBookFreeOffers == True

    @clean_database
    def test_when_user_patching_admin_and_activation_thing_set_can_book_free_offers_true_for_booking_user(self, app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_thing_offer(venue, thing_type=ThingType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        db.session.refresh(user)
        assert response.status_code == 204
        assert user.canBookFreeOffers == True

    @clean_database
    def test_when_user_patching_admin_and_no_deposit_for_booking_user_add_500_eur_deposit(self, app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_event_offer(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
        assert response.status_code == 204
        assert len(deposits_for_user) == 1
        assert deposits_for_user[0].amount == 500
        assert user.canBookFreeOffers == True

    @clean_database
    def test_when_user_patching_admin_and_deposit_for_booking_do_not_add_new_deposit_and_return_status_code_405(self,
                                                                                                                app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_event_offer(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        deposit = create_deposit(user, datetime.utcnow(), amount=500)
        PcObject.check_and_save(booking, user_offerer, deposit)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
        assert response.status_code == 405
        assert len(deposits_for_user) == 1
        assert deposits_for_user[0].amount == 500

    @clean_database
    def test_when_user_patching_not_admin_status_code_403(self, app):
        # Given
        user = create_user()
        pro_user = create_user(email='pro@email.fr', is_admin=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_event_offer(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.check_and_save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        assert response.status_code == 403
