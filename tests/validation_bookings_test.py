import pytest

from domain.expenses import SUBVENTION_PHYSICAL_THINGS, SUBVENTION_DIGITAL_THINGS
from models import ApiErrors
from utils.test_utils import create_booking_for_event, create_booking_for_thing
from validation.bookings import check_expenses_limits


@pytest.mark.standalone
def test_check_expenses_limits_raises_an_error_when_physical_limit_is_reached_for_things():
    # given
    expenses = {
        'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': 190},
        'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': 190}
    }
    booking = create_booking_for_thing(url=None, amount=6, quantity=2)
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
