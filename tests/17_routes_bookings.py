from datetime import datetime, timedelta

from models import User, Offerer, Thing, Recommendation, Offer, PcObject, Deposit, Venue
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth


def test_10_create_booking():
    booking_json = {
        'offerId': humanize(2),
        'recommendationId': humanize(1),
        'amount': 0
    }
    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    print(r_create.json())
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/bookings/'+id)
    assert r_check.status_code == 200
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]


def test_11_create_booking_should_not_work_past_limit_date(app):
    expired_offer = Offer()
    expired_offer.venueId = 1
    expired_offer.offererId = 1
    expired_offer.thingId = 1
    expired_offer.price = 0
    expired_offer.bookingLimitDatetime = datetime.utcnow() - timedelta(seconds=1)
    PcObject.check_and_save(expired_offer)

    booking_json = {
        'offerId': humanize(expired_offer.id),
        'recommendationId': humanize(1)
    }

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'date limite' in r_create.json()['global'][0]


def test_12_create_booking_should_work_before_limit_date(app):
    ok_offer = Offer()
    ok_offer.venueId = 1
    ok_offer.offererId = 1
    ok_offer.thingId = 1
    ok_offer.price = 0
    ok_offer.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    PcObject.check_and_save(ok_offer)

    booking_json = {
        'offerId': humanize(ok_offer.id),
        'recommendationId': humanize(1)
    }

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/bookings/'+id)
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]


def test_13_create_booking_should_not_work_if_too_many_bookings(app):
    too_many_bookings_offer = Offer()
    too_many_bookings_offer.venueId = 1
    too_many_bookings_offer.offererId = 1
    too_many_bookings_offer.thingId = 1
    too_many_bookings_offer.price = 0
    too_many_bookings_offer.available = 0
    too_many_bookings_offer.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    PcObject.check_and_save(too_many_bookings_offer)

    booking_json = {
        'offerId': humanize(too_many_bookings_offer.id),
        'recommendationId': humanize(1)
    }

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    print(r_create.json())
    assert 'global' in r_create.json()
    assert 'quantité disponible' in r_create.json()['global'][0]


def test_14_create_booking_should_work_if_user_can_book():
    booking_json = {
        'offerId': humanize(2),
        'recommendationId': humanize(1),
        'amount': 0
    }
    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201


def test_15_create_booking_should_not_work_if_user_can_not_book():
    # with default admin user
    booking_json = {
        'offerId': humanize(3),
        'recommendationId': humanize(1),
        'amount': 0
    }
    r_create = req_with_auth().post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400


def test_16_create_booking_should_not_work_if_not_enough_credit(app):
    #Given
    user = User()
    user.publicName = 'Test'
    user.email = 'test07@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    PcObject.check_and_save(user)

    offerer = Offerer()
    offerer.name = 'Test offerer'
    offerer.postalCode = '93000'
    offerer.address = '2 Test adress'
    offerer.city = 'Test city'
    PcObject.check_and_save(offerer)

    thing = Thing()
    thing.type = 'Book'
    thing.name = 'Test name'
    thing.extraData = {'author': 'Test Author'}
    PcObject.check_and_save(thing)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test adress'
    venue.city= 'Test city'
    venue.managingOffererId = offerer.id
    PcObject.check_and_save(venue)

    offer = Offer()
    offer.thingId = thing.id
    offer.offererId = offerer.id
    offer.price = 200
    offer.venueId = venue.id
    offer.available = 50
    PcObject.check_and_save(offer)

    recommendation = Recommendation()
    recommendation.userId = user.id
    recommendation.thingId = thing.id
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 0
    deposit.userId = user.id
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    booking_json = {
        "offerId": humanize(offer.id),
        "recommendationId": humanize(recommendation.id),
        "userId": humanize(user.id),
        "amount": float(offer.price)
    }

    # When
    r_create = req_with_auth('test07@email.com', 'testpsswd').post(API_URL + '/bookings', json=booking_json)

    # Then
    assert r_create.status_code == 400
    assert 'insufficientFunds' in r_create.json()

    PcObject.delete(deposit)
    PcObject.delete(recommendation)
    PcObject.delete(offer)
    PcObject.delete(venue)
    PcObject.delete(thing)
    PcObject.delete(offerer)
    PcObject.delete(user)
