import pytest

from domain.payments import create_payment_for_booking
from models import Booking


@pytest.mark.standalone
def test_create_payment_for_booking():
    # given
    booking = Booking()

    # when
    payment = create_payment_for_booking(booking)

    # then
    assert payment.booking == booking
