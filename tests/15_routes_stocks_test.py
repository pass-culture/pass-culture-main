from datetime import datetime, timedelta

import pytest

from models.booking import Booking
from models.event_occurrence import EventOccurrence
from models.stock import Stock
from models.pc_object import PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import req_with_auth, API_URL, create_user, create_offerer, create_venue, \
    create_stock_with_event_offer, create_booking

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


@clean_database
@pytest.mark.standalone
def test_13_number_of_avilable_stocks_cannot_be_updated_below_number_of_already_existing_bookings(app):
    # Given
    user = create_user(email='email@test.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=0)
    stock.available = 1
    booking = create_booking(user, stock, venue, recommendation=None)
    PcObject.check_and_save(booking)

    stock_id = stock.id

    # When
    r_update = req_with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock_id),
                                                                 json={'available': 0})

    # Then
    assert r_update.status_code == 400
    assert 'available' in r_update.json()


@clean_database
@pytest.mark.standalone
def test_14_should_not_create_stock_if_booking_limit_datetime_after_event_occurrence(app):
    #Given
    from models.pc_object import serialize
    user = create_user(email='email@test.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    PcObject.check_and_save(stock, user)

    stockId = stock.id

    serialized_date = serialize(stock.eventOccurrence.beginningDatetime + timedelta(days=1))

    #When
    r_update = req_with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stockId),
                                     json={'bookingLimitDatetime': serialized_date})

    #Then
    assert r_update.status_code == 400
    assert 'bookingLimitDatetime' in r_update.json()


@clean_database
@pytest.mark.standalone
def test_user_with_no_rights_should_not_be_able_to_patch_stocks(app):
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    PcObject.check_and_save(user, stock)

    # When
    r_update = req_with_auth('test@email.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock.id),
                                     json={'available': 5})

    # Then
    assert r_update.status_code == 400
    assert 'Cette structure n\'est pas enregistrée chez cet utilisateur.' in r_update.json()
