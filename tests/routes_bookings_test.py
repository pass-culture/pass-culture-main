from datetime import datetime, timedelta

import pytest

from models import User, Offerer, Recommendation, Stock, PcObject, Deposit, Venue
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth, create_stock_with_thing_offer, \
    create_thing_offer, create_deposit, create_stock_with_event_offer, create_venue, create_offerer, \
    create_recommendation, create_user


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_past_limit_date(app):
    offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')

    venue = create_venue(offerer, 'reservations@test.fr', '123 rue test', '93000', 'Test city', 'Test offerer', '93')

    thing_offer = create_thing_offer()

    expired_stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, thing_offer=thing_offer, price=0)
    expired_stock.bookingLimitDatetime = datetime.utcnow() - timedelta(seconds=1)
    PcObject.check_and_save(expired_stock)

    user = create_user('test name', '93', 'test@mail.com', password='psswd123')
    PcObject.check_and_save(user)

    recommendation = create_recommendation(thing_offer, user)

    booking_json = {
        'stockId': humanize(expired_stock.id),
        'recommendationId': humanize(recommendation.id)
    }

    r_create = req_with_auth('test@mail.com', password='psswd123').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'date limite' in r_create.json()['global'][0]


@clean_database
@pytest.mark.standalone
def test_create_booking_should_work_before_limit_date(app):
    offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
    venue = create_venue(offerer, 'reservations@test.fr', '123 rue test', '93000', 'Test city', 'Test offerer', '93')
    ok_stock = create_stock_with_event_offer(offerer=offerer,
                                             venue=venue, price=0)
    ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    PcObject.check_and_save(ok_stock)

    user = create_user('test name', '93', 'test@mail.com', password='psswd123')
    PcObject.check_and_save(user)

    recommendation = create_recommendation(offer=ok_stock.offer, user=user)
    PcObject.check_and_save(recommendation)

    booking_json = {
        'stockId': humanize(ok_stock.id),
        'recommendationId': humanize(recommendation.id)
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
    venue = create_venue(offerer, 'reservations@test.fr', '123 rue test', '93000', 'Test city', 'Test offerer', '93')
    too_many_bookings_stock = create_stock_with_thing_offer(offerer=Offerer(), venue=venue, thing_offer=None)
    too_many_bookings_stock.available = 0
    PcObject.check_and_save(too_many_bookings_stock)

    user = create_user('Toto', '93', 'test@email.com', password='mdppsswd')
    PcObject.check_and_save(user)

    recommendation = create_recommendation(offer=too_many_bookings_stock.offer, user=user)
    PcObject.check_and_save(recommendation)

    booking_json = {
        'stockId': humanize(too_many_bookings_stock.id),
        'recommendationId': humanize(recommendation.id)
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
    venue = create_venue(offerer, 'booking@email.com', '1 fake street', '93000', 'False city', 'venue name', '93')
    thing_offer = create_thing_offer()

    user = create_user('Toto', '93', 'test@email.com', password='mdppsswd')
    PcObject.check_and_save(user)

    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=50)
    PcObject.check_and_save(stock)

    recommendation = create_recommendation(thing_offer, user)
    PcObject.check_and_save(recommendation)

    deposit = create_deposit(user, datetime.utcnow(), amount=50)
    deposit.save()

    booking_json = {
        'stockId': humanize(stock.id),
        'recommendationId': humanize(recommendation.id),
    }
    r_create = req_with_auth('test@email.com', 'mdppsswd').post(API_URL + '/bookings', json=booking_json)
    print(r_create.json())
    assert r_create.status_code == 201


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_for_free_offer_if_not_userCanBookFreeOffers(app):
    # Given
    user = create_user('Test', '93', 'cannotBook_freeOffers@email.com', can_book_free_offers=False,
                       password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                             name='Test offerer')
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = create_venue(offerer=offerer, booking_email='booking@email.com', address='1 Test address',
                         postal_code='93000', city='Test city', name='Venue name', departement_code='93')
    PcObject.check_and_save(venue)

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
        "userId": humanize(user.id)
    }

    # When
    r_create = req_with_auth('cannotBook_freeOffers@email.com', 'testpsswd').post(API_URL + '/bookings', json=booking_json)

    # Then
    assert r_create.status_code == 400
    assert 'cannotBookFreeOffers' in r_create.json()


@clean_database
@pytest.mark.standalone
def test_create_booking_should_not_work_if_not_enough_credit(app):
    # Given
    user = create_user('Test', '93', 'insufficient_funds_test@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                             name='Test offerer')
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = create_venue(offerer=offerer, booking_email='booking@email.com', address='1 Test address',
                         postal_code='93000', city='Test city', name='Venue name', departement_code='93')
    PcObject.check_and_save(venue)

    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=200)
    PcObject.check_and_save(stock)

    recommendation = create_recommendation(thing_offer, user)
    PcObject.check_and_save(recommendation)

    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(user, deposit_date, amount=0)
    PcObject.check_and_save(deposit)

    booking_json = {
        "stockId": humanize(stock.id),
        "recommendationId": humanize(recommendation.id),
        "userId": humanize(user.id),
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
    #Given
    user = create_user('Test', '93', 'sufficient_funds@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                             name='Test offerer')
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = create_venue(offerer, 'reservations@test.fr', '123 rue test', '93000', 'Test city', 'Test offerer', '93')
    PcObject.check_and_save(venue)

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
        "userId": humanize(user.id),
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
    user = create_user('Test', '93', 'can_book_paid_offers@email.com', can_book_free_offers=False, password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer(siren='899999768', address='2 Test adress', city='Test city', postal_code='93000',
                             name='Test offerer')
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = create_venue(offerer, 'reservations@test.fr', '123 rue test', '93000', 'Test city', 'Test offerer', '93')
    PcObject.check_and_save(venue)

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
        "userId": humanize(user.id),
    }

    # When
    r_create = req_with_auth('can_book_paid_offers@email.com', 'testpsswd').post(API_URL + '/bookings', json=booking_json)
    r_create_json = r_create.json()

    # Then
    assert r_create.status_code == 201
    assert r_create_json['amount'] == 10.0
    assert r_create_json['quantity'] == 1
