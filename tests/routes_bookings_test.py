from datetime import datetime, timedelta

import pytest

from models.db import db
from models import Booking, Offerer, PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth, create_stock_with_thing_offer, \
    create_thing_offer, create_deposit, create_stock_with_event_offer, create_venue, create_offerer, \
    create_recommendation, create_user, create_booking


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_past_limit_date(app):
    offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')

    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')

    thing_offer = create_thing_offer(venue)

    expired_stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, thing_offer=thing_offer, price=0)
    expired_stock.bookingLimitDatetime = datetime.utcnow() - timedelta(seconds=1)
    PcObject.check_and_save(expired_stock)

    user = create_user(email='test@mail.com', password='psswd123')
    PcObject.check_and_save(user)

    recommendation = create_recommendation(thing_offer, user)

    booking_json = {
        'stockId': humanize(expired_stock.id),
        'recommendationId': humanize(recommendation.id),
        'quantity': 1
    }

    r_create = req_with_auth('test@mail.com', password='psswd123').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'date limite' in r_create.json()['global'][0]


@clean_database
@pytest.mark.standalone
def test_create_booking_should_work_before_limit_date(app):
    offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    ok_stock = create_stock_with_event_offer(offerer=offerer,
                                             venue=venue, price=0)
    ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    PcObject.check_and_save(ok_stock)

    user = create_user(email='test@mail.com', password='psswd123')
    PcObject.check_and_save(user)

    recommendation = create_recommendation(offer=ok_stock.offer, user=user)
    PcObject.check_and_save(recommendation)

    booking_json = {
        'stockId': humanize(ok_stock.id),
        'recommendationId': humanize(recommendation.id),
        'quantity': 1
    }

    r_create = req_with_auth(email='test@mail.com', password='psswd123').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth(email='test@mail.com', password='psswd123').get(API_URL + '/bookings/' + id)
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_if_too_many_bookings(app):
    offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    too_many_bookings_stock = create_stock_with_thing_offer(offerer=Offerer(), venue=venue, thing_offer=None)
    too_many_bookings_stock.available = 0
    PcObject.check_and_save(too_many_bookings_stock)

    user = create_user(email='test@email.com', password='mdppsswd')
    PcObject.check_and_save(user)

    recommendation = create_recommendation(offer=too_many_bookings_stock.offer, user=user)
    PcObject.check_and_save(recommendation)

    booking_json = {
        'stockId': humanize(too_many_bookings_stock.id),
        'recommendationId': humanize(recommendation.id),
        'quantity': 1
    }

    r_create = req_with_auth('test@email.com', 'mdppsswd').post(API_URL + '/bookings', json=booking_json)

    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'quantité disponible' in r_create.json()['global'][0]


@clean_database
@pytest.mark.standalone
def test_create_booking_should_work_if_user_can_book_and_enough_credit(app):
    # Given
    offerer = create_offerer('819202819', '1 Fake Address', 'Fake city', '93000', 'Fake offerer')
    venue = create_venue(offerer, 'venue name', 'booking@email.com', '1 fake street', '93000', 'False city', '93')
    thing_offer = create_thing_offer(venue)

    user = create_user(email='test@email.com', password='mdppsswd')
    PcObject.check_and_save(user)

    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=50)
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
    r_create = req_with_auth('test@email.com', 'mdppsswd').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_for_free_offer_if_not_userCanBookFreeOffers(app):
    # Given
    user = create_user(email='cannotBook_freeOffers@email.com', can_book_free_offers=False,
                       password='testpsswd')
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
    r_create = req_with_auth('cannotBook_freeOffers@email.com', 'testpsswd').post(API_URL + '/bookings',
                                                                                  json=booking_json)

    # Then
    assert r_create.status_code == 400
    assert 'cannotBookFreeOffers' in r_create.json()


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_if_not_enough_credit(app):
    # Given
    user = create_user(email='insufficient_funds_test@email.com', password='testpsswd')
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
    r_create = req_with_auth('insufficient_funds_test@email.com', 'testpsswd').post(API_URL + '/bookings',
                                                                                    json=booking_json)

    # Then
    assert r_create.status_code == 400
    assert 'insufficientFunds' in r_create.json()


@clean_database
@pytest.mark.standalone
def test_create_booking_should_work_if_enough_credit_when_userCanBookFreeOffers(app):
    # Given
    user = create_user(email='sufficient_funds@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                             name='Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    PcObject.check_and_save(venue)

    thing_offer = create_thing_offer(venue)
    PcObject.check_and_save(thing_offer)

    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=5)
    PcObject.check_and_save(stock)

    recommendation = create_recommendation(thing_offer, user)
    PcObject.check_and_save(recommendation)

    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(user, deposit_date, amount=9)
    PcObject.check_and_save(deposit)

    booking_json = {
        "stockId": humanize(stock.id),
        "recommendationId": humanize(recommendation.id),
        "quantity": 1
    }

    # When
    r_create = req_with_auth('sufficient_funds@email.com', 'testpsswd').post(API_URL + '/bookings', json=booking_json)

    # Then
    r_create_json = r_create.json()
    assert r_create.status_code == 201
    assert r_create_json['amount'] == 5.0
    assert r_create_json['quantity'] == 1


@clean_database
@pytest.mark.standalone
def test_create_booking_should_work_for_paid_offer_if_user_can_not_book_but_has_enough_credit(app):
    user = create_user(email='can_book_paid_offers@email.com', can_book_free_offers=False, password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                             name='Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
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
    r_create = req_with_auth('can_book_paid_offers@email.com', 'testpsswd').post(API_URL + '/bookings',
                                                                                 json=booking_json)
    r_create_json = r_create.json()

    # Then
    assert r_create.status_code == 201
    assert r_create_json['amount'] == 10.0
    assert r_create_json['quantity'] == 1


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_if_only_public_credit_and_100_euros_limit_physical_thing_reached(app):
    # Given
    user = create_user(email='test@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer()
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer)
    PcObject.check_and_save(venue)

    thing_offer = create_thing_offer(venue)
    PcObject.check_and_save(thing_offer)

    stock_1 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=90)
    stock_2 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=9)
    PcObject.check_and_save(stock_1, stock_2)

    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(user, deposit_date, amount=500, source='public')
    PcObject.check_and_save(deposit)

    booking_1 = create_booking(user, stock_1, venue, recommendation=None)
    PcObject.check_and_save(booking_1)

    recommendation = create_recommendation(thing_offer, user)
    PcObject.check_and_save(recommendation)

    booking_json = {
        "stockId": humanize(stock_2.id),
        "recommendationId": humanize(recommendation.id),
        "quantity": 2
    }

    # When
    response = req_with_auth('test@email.com', 'testpsswd').post(API_URL + '/bookings',
                                                                 json=booking_json)
    # Then
    error_message = response.json()
    assert response.status_code == 400
    assert error_message['global'] == ['La limite de 100 € pour les biens culturels ' \
                                       'ne vous permet pas de réserver']


@clean_database
@pytest.mark.standalone
def test_create_booking_returns_bad_request_if_no_stock_id_is_given(app):
    # Given
    user = create_user(email='test@email.com', password='testpsswd')
    PcObject.check_and_save(user)
    booking_json = {
        'stockId': None,
        'recommendationId': 'AFQA',
        'quantity': 2
    }

    # When
    response = req_with_auth('test@email.com', 'testpsswd').post(API_URL + '/bookings',
                                                                 json=booking_json)
    # Then
    error_message = response.json()
    assert response.status_code == 400
    assert error_message['stockId'] == ['Vous devez préciser un identifiant d\'offre']


@clean_database
@pytest.mark.standalone
def test_create_booking_returns_bad_request_if_no_quantity_is_given(app):
    # Given
    user = create_user(email='test@email.com', password='testpsswd')
    PcObject.check_and_save(user)
    booking_json = {
        'stockId': 'AE',
        'recommendationId': 'AFQA',
        'quantity': None
    }

    # When
    response = req_with_auth('test@email.com', 'testpsswd').post(API_URL + '/bookings',
                                                                 json=booking_json)
    # Then
    error_message = response.json()
    assert response.status_code == 400
    assert error_message['quantity'] == ['Vous devez préciser une quantité pour la réservation']


@clean_database
@pytest.mark.standalone
def test_cancel_booking_returns_200_and_effectively_marks_the_booking_as_cancelled(app):
    # Given
    user = create_user(email='test@email.com', password='testpsswd')
    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(user, deposit_date, amount=500)
    booking = create_booking(user)
    PcObject.check_and_save(user, deposit, booking)

    # When
    response = req_with_auth(user.email, user.clearTextPassword)\
                 .delete(API_URL + '/bookings/' + humanize(booking.id))

    # Then
    assert response.status_code == 200
    db.session.refresh(booking)
    assert booking.isCancelled


@clean_database
@pytest.mark.standalone
def test_cancel_booking_returns_404_if_booking_does_not_exist(app):
    # Given
    user = create_user(email='test@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    # When
    response = req_with_auth(user.email, user.clearTextPassword)\
                 .delete(API_URL + '/bookings/AX')

    # Then
    assert response.status_code == 404


@clean_database
@pytest.mark.standalone
def test_cancel_booking_for_other_users_returns_403_and_does_not_mark_the_booking_as_cancelled(app):
    # Given
    other_user = create_user(email='test2@email.com', password='testpsswd')
    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(other_user, deposit_date, amount=500)
    booking = create_booking(other_user)
    user = create_user(email='test@email.com', password='testpsswd')
    PcObject.check_and_save(user, other_user, deposit, booking)

    # When
    response = req_with_auth(user.email, user.clearTextPassword)\
                 .delete(API_URL + '/bookings/' + humanize(booking.id))

    # Then
    assert response.status_code == 403
    db.session.refresh(booking)
    assert not booking.isCancelled


@clean_database
@pytest.mark.standalone
def test_an_admin_cancelling_a_users_booking_returns_200_and_effectively_marks_the_booking_as_cancelled(app):
    # Given
    admin_user = create_user(email='test@email.com', password='testpsswd', is_admin=True, can_book_free_offers=False)
    other_user = create_user(email='test2@email.com', password='testpsswd')
    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(other_user, deposit_date, amount=500)
    booking = create_booking(other_user)
    PcObject.check_and_save(admin_user, other_user, deposit, booking)

    # When
    response = req_with_auth(admin_user.email, admin_user.clearTextPassword)\
                 .delete(API_URL + '/bookings/' + humanize(booking.id))

    # Then
    assert response.status_code == 200
    db.session.refresh(booking)
    assert booking.isCancelled
