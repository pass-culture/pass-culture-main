import pytest
from domain.payments import create_payment_for_booking
from models.payment import Payment
from utils.test_utils import create_booking, create_user


@pytest.mark.standalone
def test_create_payment_for_booking():
    # Given
    user = create_user()
    booking = create_booking(user, stock=None)

    # When
    payment_for_booking = create_payment_for_booking(booking)

    # Then
    assert type(payment_for_booking) == Payment()