""" repository booking queries test """
from datetime import datetime, timedelta

import pytest

from models import PcObject
from repository.booking_queries import find_all_ongoing_bookings_by_stock, \
                                       find_offerer_bookings
from tests.conftest import clean_database
from utils.test_utils import create_booking, \
                             create_deposit, \
                             create_offerer, \
                             create_stock_with_event_offer, \
                             create_stock_with_thing_offer, \
                             create_user, \
                             create_venue


@clean_database
@pytest.mark.standalone
def test_find_all_by_offerer_with_event_and_things(app):
    # given
    user = create_user()
    now = datetime.utcnow()
    create_deposit(user, now, amount=1600)
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    venue1 = create_venue(offerer1)
    venue2 = create_venue(offerer2)
    stock1 = create_stock_with_event_offer(offerer1, venue1, price=200)
    stock2 = create_stock_with_thing_offer(offerer1, venue1, thing_offer=None, price=300)
    stock3 = create_stock_with_thing_offer(offerer2, venue2, thing_offer=None, price=400)
    booking1 = create_booking(user, stock1, venue1, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock2, venue1, recommendation=None, quantity=1)
    booking3 = create_booking(user, stock3, venue2, recommendation=None, quantity=2)
    PcObject.check_and_save(booking1, booking2, booking3)

    # when
    bookings = find_offerer_bookings(offerer1.id)

    # then
    assert bookings[0].id > bookings[1].id
    assert booking1 in bookings
    assert booking2 in bookings
    assert booking3 not in bookings


@clean_database
@pytest.mark.standalone
def test_find_all_ongoing_bookings(app):
    # Given
    offerer = create_offerer(siren='985281920')
    PcObject.check_and_save(offerer)
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=0)
    user = create_user()
    cancelled_booking = create_booking(user, stock, is_cancelled=True)
    validated_booking = create_booking(user, stock, is_used=True)
    ongoing_booking = create_booking(user, stock, is_cancelled=False, is_used=False)
    PcObject.check_and_save(ongoing_booking)
    PcObject.check_and_save(validated_booking)
    PcObject.check_and_save(cancelled_booking)


    # When
    all_ongoing_bookings = find_all_ongoing_bookings_by_stock(stock)

    # Then
    assert all_ongoing_bookings == [ongoing_booking]
