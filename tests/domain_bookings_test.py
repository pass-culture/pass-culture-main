import pytest

from domain.bookings import check_expenses_limits
from domain.expenses import SUBVENTION_PHYSICAL_THINGS, SUBVENTION_DIGITAL_THINGS
from models import Booking, ApiErrors, Stock, Thing, Offer, Event


@pytest.mark.standalone
def test_check_expenses_limits_raises_an_error_when_physical_limit_is_reached_for_things():
    # given
    expenses = {
        'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': 90},
        'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': 190}
    }
    booking = create_booking_for_thing(url=None, amount=9, quantity=2)
    stock = booking.stock

    # when
    with pytest.raises(ApiErrors) as api_errors:
        check_expenses_limits(expenses, booking, stock)

    # then
    assert api_errors.value.errors['global'] == ['La limite de %s € pour les biens culturels ne vous permet pas ' \
                                                 'de réserver' % SUBVENTION_PHYSICAL_THINGS]


@pytest.mark.standalone
def test_check_expenses_limits_raises_an_error_when_digital_limit_is_reached_for_things():
    # given
    expenses = {
        'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': 90},
        'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': 190}
    }
    booking = create_booking_for_thing(url='http://truc', amount=9, quantity=2)
    stock = booking.stock

    # when
    with pytest.raises(ApiErrors) as api_errors:
        check_expenses_limits(expenses, booking, stock)

    # then
    assert api_errors.value.errors['global'] == ['La limite de %s € pour les offres numériques ne vous permet pas ' \
                                                 'de réserver' % SUBVENTION_DIGITAL_THINGS]


@pytest.mark.standalone
def test_check_expenses_limits_does_not_raise_an_error_when_booking_for_an_event():
    # given
    expenses = {
        'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': 90},
        'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': 190}
    }
    booking = create_booking_for_event(amount=9, quantity=2)
    stock = booking.stock

    # when
    try:
        check_expenses_limits(expenses, booking, stock)
    except ApiErrors:
        # then
        pytest.fail('Booking for events must not raise any exceptions')


def create_booking_for_thing(url=None, amount=50, quantity=1):
    thing = Thing(from_dict={'url': url})
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.thing = thing
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    return booking


def create_booking_for_event(amount=50, quantity=1):
    event = Event()
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.event = event
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    return booking
