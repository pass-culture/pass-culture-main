from datetime import datetime, timedelta
import pytest
from domain.payments import create_initial_payment_for_booking
from models.payment import Payment, PaymentType
from utils.test_utils import create_booking, create_user


@pytest.mark.standalone
def test_create_payment_for_booking():
    # Given
    user = create_user()
    booking = create_booking(user, stock=None)
    author = 'toto'
    offerer = booking.stock.resolvedOffer.venue.managingOfferer

    # When
    payment_for_booking = create_initial_payment_for_booking(booking, author)

    # Then
    assert type(payment_for_booking) == Payment
    assert payment_for_booking.type == PaymentType.INITIAL
    # assert payment_for_booking.status is None
    assert payment_for_booking.offerer == offerer
    assert payment_for_booking.author == author
    assert payment_for_booking.comment is None
    assert payment_for_booking.booking == booking
    assert payment_for_booking.iban == offerer.iban
    # assert payment_for_booking.dateStatus < datetime.utcnow()
    # assert payment_for_booking.dateStatus > datetime.utcnow() - timedelta(minutes=1)
