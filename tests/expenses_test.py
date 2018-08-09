from datetime import timedelta, datetime

import pytest

from models import Booking
from tests.conftest import clean_database
from utils.test_utils import create_user, create_stock_with_thing_offer, create_offerer, create_venue, \
    create_thing_offer, create_deposit, create_stock_with_event_offer
from expenses.expenses import get_expenses


@pytest.mark.standalone
@clean_database
def test_get_expenses_should_return_a_dictionary(app):
    # Given
    user = create_user('test@email.com', 'name', '93')
    user.save()

    # When
    expenses = get_expenses(user)

    # Then
    assert type(expenses) == dict


@pytest.mark.standalone
@clean_database
def test_get_expenses_should_have_max_500_and_actual_100_at_key_all_when_sum_bookings_amount_100(app):
    # Given
    user = create_user('test@email.com', 'name', '93')
    user.save()

    offerer = create_offerer('123456789', '1 rue Address', 'Test city', '93000', 'Name')
    offerer.save()

    venue = create_venue(offerer, 'booking@email.com', '7 rue Address', '93000', 'Test city', 'name', '93')
    venue.save()

    stock_1 = create_stock_with_thing_offer(offerer, venue, price=60)
    stock_1.save()

    stock_2 = create_stock_with_event_offer(offerer, venue, price=40)
    stock_2.save()

    deposit = create_deposit(user, date=datetime.utcnow() - timedelta(minutes=2), amount=500)
    deposit.save()

    booking_1 = Booking()
    booking_1.stock = stock_1
    booking_1.user = user
    booking_1.token = '56789'
    booking_1.amount = stock_1.price
    booking_1.save()

    booking_2 = Booking()
    booking_2.stock = stock_2
    booking_2.user = user
    booking_2.token = '12340'
    booking_2.amount = stock_2.price
    booking_2.save()

    # When
    expenses = get_expenses(user)

    # Then
    assert expenses['all'] == {'max': 500, 'actual': 100}


@pytest.mark.standalone
@clean_database
def test_get_expenses_should_have_max_500_and_actual_150_at_key_all_when_sum_bookings_amount_150(app):
    # Given
    user = create_user('test@email.com', 'name', '93')
    user.save()

    offerer = create_offerer('123456789', '1 rue Address', 'Test city', '93000', 'Name')
    offerer.save()

    venue = create_venue(offerer, 'booking@email.com', '7 rue Address', '93000', 'Test city', 'name', '93')
    venue.save()

    stock_1 = create_stock_with_thing_offer(offerer, venue, price=90)
    stock_1.save()

    stock_2 = create_stock_with_event_offer(offerer, venue, price=60)
    stock_2.save()

    deposit = create_deposit(user, date=datetime.utcnow() - timedelta(minutes=2), amount=500)
    deposit.save()

    booking_1 = Booking()
    booking_1.stock = stock_1
    booking_1.user = user
    booking_1.token = '56789'
    booking_1.amount = stock_1.price
    booking_1.save()

    booking_2 = Booking()
    booking_2.stock = stock_2
    booking_2.user = user
    booking_2.token = '12340'
    booking_2.amount = stock_2.price
    booking_2.save()

    # When
    expenses = get_expenses(user)

    # Then
    assert expenses['all'] == {'max': 500, 'actual': 150}


@pytest.mark.standalone
@clean_database
def test_get_expenses_should_have_max_200_and_actual_50_at_key_digital_when_sum_amount_bookings_filtered_by_stock_digital_50(app):
    # Given
    user = create_user('test@email.com', 'name', '93')
    user.save()

    offerer = create_offerer('123456789', '1 rue Address', 'Test city', '93000', 'Name')
    offerer.save()

    venue = create_venue(offerer, 'booking@email.com', '7 rue Address', '93000', 'Test city', 'name', '93')
    venue.save()

    thing_offer = create_thing_offer()
    thing_offer.save()

    stock_1 = create_stock_with_thing_offer(offerer, venue, thing_offer, price=50)
    stock_1.save()

    deposit = create_deposit(user, date=datetime.utcnow() - timedelta(minutes=2), amount=500)
    deposit.save()

    booking_1 = Booking()
    booking_1.stock = stock_1
    booking_1.user = user
    booking_1.token = '56789'
    booking_1.amount = stock_1.price
    booking_1.save()

    booking_2 = Booking()
    booking_2.stock = stock_2
    booking_2.user = user
    booking_2.token = '12340'
    booking_2.amount = stock_2.price
    booking_2.save()

    # When
    expenses = get_expenses(user)

    # Then
    assert expenses['all'] == {'max': 500, 'actual': 150}