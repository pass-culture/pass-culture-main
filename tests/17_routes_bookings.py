from datetime import datetime, timedelta

from models import User, Offerer, Recommendation, Stock, PcObject, Deposit, Venue
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth, create_stock_with_thing_offer, \
    create_thing_offer, create_deposit


def test_11_create_booking_should_not_work_past_limit_date(app):
    expired_stock = create_stock_with_thing_offer(price=0)
    expired_stock.bookingLimitDatetime = datetime.utcnow() - timedelta(seconds=1)
    PcObject.check_and_save(expired_stock)

    booking_json = {
        'stockId': humanize(expired_stock.id),
        'recommendationId': humanize(1)
    }

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'date limite' in r_create.json()['global'][0]


def test_12_create_booking_should_work_before_limit_date(app):
    ok_stock = Stock()
    ok_stock.venueId = 1
    ok_stock.offerId = 1
    ok_stock.price = 0
    ok_stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    PcObject.check_and_save(ok_stock)

    booking_json = {
        'stockId': humanize(ok_stock.id),
        'recommendationId': humanize(1)
    }

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/bookings/' + id)
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]


def test_13_create_booking_should_not_work_if_too_many_bookings(app):
    too_many_bookings_stock = create_stock_with_thing_offer()
    too_many_bookings_stock.available = 0
    PcObject.check_and_save(too_many_bookings_stock)

    recommendation = Recommendation()
    recommendation.user = User.query.filter_by(email='pctest.jeune.93@btmx.fr').first()
    recommendation.offer = too_many_bookings_stock.offer
    PcObject.check_and_save(recommendation)

    booking_json = {
        'stockId': humanize(too_many_bookings_stock.id),
        'recommendationId': humanize(recommendation.id)
    }

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'quantité disponible' in r_create.json()['global'][0]


def test_14_create_booking_should_work_if_user_can_book_and_enough_credit(app):
    booking_json = {
        'stockId': humanize(2),
        'recommendationId': humanize(1),
    }
    user = User.query.filter_by(email='pctest.jeune.93@btmx.fr').first()
    deposit = create_deposit(user, amount=50)
    deposit.save()

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201


def test_15_create_booking_should_not_work_for_free_offer_if_not_userCanBookFreeOffers(app):
    # Given
    user = User()
    user.publicName = 'Test'
    user.email = 'cannotBook_freeOffers@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    user.canBookFreeOffers = False
    PcObject.check_and_save(user)

    offerer = Offerer()
    offerer.name = 'Offerer'
    offerer.postalCode = '93000'
    offerer.address = '99 Test adress'
    offerer.city = 'Test city'
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    stock = Stock()
    stock.offer = thing_offer
    stock.offer.venue = venue
    stock.offerer = offerer
    stock.price = 0
    stock.available = 50
    PcObject.check_and_save(stock)

    recommendation = Recommendation()
    recommendation.offer = thing_offer
    recommendation.user = user
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 500
    deposit.userId = user.id
    deposit.source = 'public'
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


def test_16_create_booking_should_not_work_if_not_enough_credit(app):
    # Given
    user = User()
    user.publicName = 'Test'
    user.email = 'insufficient_funds_test@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    PcObject.check_and_save(user)

    offerer = Offerer()
    offerer.name = 'Test offerer'
    offerer.postalCode = '93000'
    offerer.address = '2 Test adress'
    offerer.city = 'Test city'
    offerer.siren = '899999768'
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    stock = Stock()
    stock.offer = thing_offer
    stock.offer.venue = venue
    stock.offerer = offerer
    stock.price = 200
    stock.available = 50
    PcObject.check_and_save(stock)

    recommendation = Recommendation()
    recommendation.offer = thing_offer
    recommendation.user = user
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 0
    deposit.user = user
    deposit.source = 'public'
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

    PcObject.delete(deposit)
    PcObject.delete(recommendation)
    PcObject.delete(stock)
    PcObject.delete(venue)
    PcObject.delete(thing_offer)
    PcObject.delete(offerer)
    PcObject.delete(user)


def test_17_create_booking_should_work_if_enough_credit_when_userCanBookFreeOffers(app):
    #Given
    user = User()
    user.publicName = 'Test'
    user.email = 'sufficient_funds@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    PcObject.check_and_save(user)

    offerer = Offerer()
    offerer.name = 'Test offerer'
    offerer.postalCode = '93000'
    offerer.address = '2 Test adress'
    offerer.city = 'Test city'
    offerer.siren = '799999999'
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    stock = Stock()
    stock.offer = thing_offer
    stock.offer.venue = venue
    stock.offerer = offerer
    stock.price = 5
    stock.available = 50
    PcObject.check_and_save(stock)

    recommendation = Recommendation()
    recommendation.offer = thing_offer
    recommendation.user = user
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 9
    deposit.user = user
    deposit.source = 'public'
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


def test_18_create_booking_should_work_for_paid_offer_if_user_can_not_book_but_has_enough_credit(app):
    user = User()
    user.publicName = 'Test'
    user.email = 'can_book_paid_offers@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    user.canBookFreeOffers = False
    PcObject.check_and_save(user)

    offerer = Offerer()
    offerer.name = 'Offerer'
    offerer.postalCode = '93000'
    offerer.address = '99 Test adress'
    offerer.city = 'Test city'
    PcObject.check_and_save(offerer)

    thing_offer = create_thing_offer()
    PcObject.check_and_save(thing_offer)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    stock = Stock()
    stock.offer = thing_offer
    stock.offer.venue = venue
    stock.offerer = offerer
    stock.price = 10
    stock.available = 50
    PcObject.check_and_save(stock)

    recommendation = Recommendation()
    recommendation.occasion = thing_offer
    recommendation.user = user
    PcObject.check_and_save(recommendation)
    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 500
    deposit.userId = user.id
    deposit.source = 'public'
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
