from datetime import datetime, timedelta

from models import User, Offerer, Recommendation, Offer, PcObject, Deposit, Venue
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth, create_offer_with_thing_occasion, \
    create_thing_occasion, create_deposit


def test_11_create_booking_should_not_work_past_limit_date(app):
    expired_offer = create_offer_with_thing_occasion(price=0)
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
    ok_offer.occasionId = 1
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
    r_check = req_with_auth().get(API_URL + '/bookings/' + id)
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]


def test_13_create_booking_should_not_work_if_too_many_bookings(app):
    too_many_bookings_offer = create_offer_with_thing_occasion()
    too_many_bookings_offer.available = 0
    PcObject.check_and_save(too_many_bookings_offer)

    recommendation = Recommendation()
    recommendation.user = User.query.filter_by(email='pctest.jeune.93@btmx.fr').first()
    recommendation.occasion = too_many_bookings_offer.occasion
    PcObject.check_and_save(recommendation)

    booking_json = {
        'offerId': humanize(too_many_bookings_offer.id),
        'recommendationId': humanize(recommendation.id)
    }

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'quantité disponible' in r_create.json()['global'][0]


def test_14_create_booking_should_work_if_user_can_book_and_enough_credit(app):
    booking_json = {
        'offerId': humanize(2),
        'recommendationId': humanize(1),
    }
    user = User.query.filter_by(email='pctest.jeune.93@btmx.fr').first()
    deposit = create_deposit(user, amount=50)
    deposit.save()

    r_create = req_with_auth('pctest.jeune.93@btmx.fr').post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201


def test_15_create_booking_should_not_work_for_free_offer_if_not_userCanBookFreeOffers(app):
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

    thing_occasion = create_thing_occasion()
    PcObject.check_and_save(thing_occasion)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    offer = Offer()
    offer.occasion = thing_occasion
    offer.occasion.venue = venue
    offer.offerer = offerer
    offer.price = 0
    offer.available = 50
    PcObject.check_and_save(offer)

    recommendation = Recommendation()
    recommendation.occasion = thing_occasion
    recommendation.user = user
    PcObject.check_and_save(recommendation)

    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 500
    deposit.userId = user.id
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    booking_json = {
        "offerId": humanize(offer.id),
        "recommendationId": humanize(recommendation.id),
        "userId": humanize(user.id),
    }

    # When
    r_create = req_with_auth('cannotBook_freeOffers@email.com', 'testpsswd').post(API_URL + '/bookings', json=booking_json)

    # Then
    assert r_create.status_code == 400
    assert 'cannotBookFreeOffers' in r_create.json()


def test_17_create_booking_should_not_work_if_not_enough_credit(app):
    #Given
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
    PcObject.check_and_save(offerer)

    thing_occasion = create_thing_occasion()
    PcObject.check_and_save(thing_occasion)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    offer = Offer()
    offer.occasion = thing_occasion
    offer.occasion.venue = venue
    offer.offerer = offerer
    offer.price = 200
    offer.available = 50
    PcObject.check_and_save(offer)

    recommendation = Recommendation()
    recommendation.occasion = thing_occasion
    recommendation.user = user
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 0
    deposit.user = user
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    booking_json = {
        "offerId": humanize(offer.id),
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
    PcObject.delete(offer)
    PcObject.delete(venue)
    PcObject.delete(thing_occasion)
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
    PcObject.check_and_save(offerer)

    thing_occasion = create_thing_occasion()
    PcObject.check_and_save(thing_occasion)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    offer = Offer()
    offer.occasion = thing_occasion
    offer.occasion.venue = venue
    offer.offerer = offerer
    offer.price = 5
    offer.available = 50
    PcObject.check_and_save(offer)

    recommendation = Recommendation()
    recommendation.occasion = thing_occasion
    recommendation.user = user
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 9
    deposit.user = user
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    booking_json = {
        "offerId": humanize(offer.id),
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

    thing_occasion = create_thing_occasion()
    PcObject.check_and_save(thing_occasion)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOfferer = offerer
    PcObject.check_and_save(venue)

    offer = Offer()
    offer.occasion = thing_occasion
    offer.occasion.venue = venue
    offer.offerer = offerer
    offer.price = 5
    offer.available = 50
    PcObject.check_and_save(offer)

    recommendation = Recommendation()
    recommendation.occasion = thing_occasion
    recommendation.user = user
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 500
    deposit.userId = user.id
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    booking_json = {
        "offerId": humanize(offer.id),
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
