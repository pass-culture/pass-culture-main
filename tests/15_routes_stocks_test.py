from datetime import datetime, timedelta

from models.booking import Booking
from models.event_occurrence import EventOccurrence
from models.stock import Stock
from models.pc_object import PcObject
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth
from utils.token import random_token


def test_10_get_stocks_should_return_a_list_of_stocks():
    r = req_with_auth().get(API_URL + '/stocks')
    assert r.status_code == 200
    stocks = r.json()
    assert len(stocks) > 0


def test_11_modify_stock():
    r_before = req_with_auth().get(API_URL + '/stocks/EY')
    assert r_before.status_code == 200
    r_mod = req_with_auth().patch(API_URL + '/stocks/EY',
                                json={'price': 1234})
    assert r_mod.status_code == 200
    r_after = req_with_auth().get(API_URL + '/stocks/EY')
    assert r_after.status_code == 200
    assert r_after.json()['price'] == 1234

#TODO: check stock modification with missing items or incorrect values


def test_12_create_stock():
    stock_data = {'price': 1222,
                  'offerId': humanize(1)
                 }
    r_create = req_with_auth().post(API_URL + '/stocks/',
                                  json=stock_data)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/stocks/'+id)
    assert r_check.status_code == 200
    created_stock_data = r_check.json()
    for (key, value) in stock_data.items():
        assert created_stock_data[key] == stock_data[key]
    #TODO: check thumb presence


def test_13_update_stock_available_should_check_bookings(app):
    stock = Stock()
    stock.offerId = 1
    stock.price = 0
    stock.available = 1
    stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    PcObject.check_and_save(stock)

    stockId = stock.id

    booking = Booking()
    booking.stockId = stockId
    booking.recommendationId = 1
    booking.token = random_token()
    booking.userId = 1
    booking.amount = 0
    PcObject.check_and_save(booking)

    r_update = req_with_auth().patch(API_URL + '/stocks/'+humanize(stockId),
                                     json={'available': 0})
    assert r_update.status_code == 400
    assert 'available' in r_update.json()


def test_14_should_not_create_stock_if_event_occurrence_before_booking_limit_datetime(app):
    #Given
    from models.pc_object import serialize
    event_occurrence = EventOccurrence()
    event_occurrence.beginningDatetime = datetime.utcnow() + timedelta(days=10)
    event_occurrence.endDatetime = event_occurrence.beginningDatetime + timedelta(days=1)
    event_occurrence.offerId = 1
    event_occurrence.accessibility = bytes([0])
    PcObject.check_and_save(event_occurrence)

    event_occurrence_id = event_occurrence.id

    stock = Stock()
    stock.eventOccurrence = event_occurrence
    stock.offerId = 11
    stock.eventOccurrenceId = event_occurrence_id
    stock.price = 0
    stock.available = 5
    stock.bookingLimitDatetime = event_occurrence.beginningDatetime - timedelta(days=1)

    PcObject.check_and_save(stock)

    stockId = stock.id

    serialized_date = serialize(event_occurrence.beginningDatetime + timedelta(days=1))

    #When
    r_update = req_with_auth().patch(API_URL + '/stocks/'+humanize(stockId),
                                     json={'bookingLimitDatetime': serialized_date})

    #Then
    assert r_update.status_code == 400
    assert 'bookingLimitDatetime' in r_update.json()
