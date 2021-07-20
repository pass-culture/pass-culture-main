import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.payments.factories as payments_factories
from pcapi.models import Booking
from pcapi.scripts.booking.canceling_token_validation import canceling_token_validation


@pytest.mark.usefixtures("db_session")
def test_should_update_booking_when_valid_token_is_given_and_no_payment_associated(app):
    # Given
    token = "123456"
    booking = bookings_factories.BookingFactory(isUsed=True, status=BookingStatus.USED, token=token)

    # When
    canceling_token_validation(token=token)

    # Then
    booking = Booking.query.first()
    assert not booking.isUsed
    assert booking.status is not BookingStatus.USED
    assert booking.dateUsed is None


@pytest.mark.usefixtures("db_session")
def test_should_do_nothing_when_valid_token_is_given_but_the_booking_is_linked_to_a_payment(app):
    # Given
    token = "123456"
    booking = bookings_factories.BookingFactory(isUsed=True, status=BookingStatus.USED, token=token)
    initial_date_used = booking.dateUsed
    payments_factories.PaymentFactory(booking=booking)

    # When
    canceling_token_validation(token=token)

    # Then
    booking = Booking.query.first()
    assert booking.isUsed
    assert booking.status is BookingStatus.USED
    assert booking.dateUsed == initial_date_used
