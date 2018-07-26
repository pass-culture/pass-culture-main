from datetime import datetime, timedelta

from models.booking import Booking
from models.event_occurence import EventOccurence
from models.offer import Offer
from models.pc_object import PcObject
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth
from utils.token import random_token


def test_10_get_offers_should_return_a_list_of_offers():
    r = req_with_auth().get(API_URL + '/offers')
    assert r.status_code == 200
    offers = r.json()
    assert len(offers) > 0


def test_11_modify_offer():
    r_before = req_with_auth().get(API_URL + '/offers/EY')
    assert r_before.status_code == 200
    r_mod = req_with_auth().patch(API_URL + '/offers/EY',
                                json={'price': 1234})
    assert r_mod.status_code == 200
    r_after = req_with_auth().get(API_URL + '/offers/EY')
    assert r_after.status_code == 200
    assert r_after.json()['price'] == 1234

#TODO: check offer modification with missing items or incorrect values


def test_12_create_offer():
    offer_data = {'price': 1222,
                  'occasionId': humanize(1)
                 }
    r_create = req_with_auth().post(API_URL + '/offers/',
                                  json=offer_data)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/offers/'+id)
    assert r_check.status_code == 200
    created_offer_data = r_check.json()
    for (key, value) in offer_data.items():
        assert created_offer_data[key] == offer_data[key]
    #TODO: check thumb presence


def test_13_update_offer_available_should_check_bookings(app):
    offer = Offer()
    offer.occasionId = 1
    offer.price = 0
    offer.available = 1
    offer.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    PcObject.check_and_save(offer)

    offerId = offer.id

    booking = Booking()
    booking.offerId = offerId
    booking.recommendationId = 1
    booking.token = random_token()
    booking.userId = 1
    booking.amount = 0
    PcObject.check_and_save(booking)

    r_update = req_with_auth().patch(API_URL + '/offers/'+humanize(offerId),
                                     json={'available': 0})
    assert r_update.status_code == 400
    assert 'available' in r_update.json()


def test_14_should_not_create_offer_if_event_occurence_before_booking_limit_datetime(app):
    #Given
    from models.pc_object import serialize
    event_occurence = EventOccurence()
    event_occurence.beginningDatetime = datetime.utcnow() + timedelta(days=10)
    event_occurence.endDatetime = event_occurence.beginningDatetime + timedelta(days=1)
    event_occurence.occasionId = 1
    event_occurence.accessibility = bytes([0])
    PcObject.check_and_save(event_occurence)

    event_occurence_id = event_occurence.id

    offer = Offer()
    offer.eventOccurence = event_occurence
    offer.occasionId = 11
    offer.eventOccurenceId = event_occurence_id
    offer.price = 0
    offer.available = 5
    offer.bookingLimitDatetime = event_occurence.beginningDatetime - timedelta(days=1)

    PcObject.check_and_save(offer)

    offerId = offer.id

    serialized_date = serialize(event_occurence.beginningDatetime + timedelta(days=1))

    #When
    r_update = req_with_auth().patch(API_URL + '/offers/'+humanize(offerId),
                                     json={'bookingLimitDatetime': serialized_date})

    #Then
    assert r_update.status_code == 400
    assert 'bookingLimitDatetime' in r_update.json()
