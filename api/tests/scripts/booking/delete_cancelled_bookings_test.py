import datetime

import pytest

from pcapi.core.bookings.exceptions import CannotDeleteBookingWithReimbursementException
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import PricingStatus
from pcapi.scripts.booking.delete_cancelled_booking import delete_cancelled_booking


@pytest.mark.usefixtures("db_session")
def test_should_not_delete_booking_with_reimbursement():
    # Given
    value_date = datetime.datetime.utcnow()
    booking = bookings_factories.BookingFactory(status=bookings_models.BookingStatus.CANCELLED)
    venue = booking.venue
    finance_factories.PricingFactory(booking=booking, valueDate=value_date, status=PricingStatus.PROCESSED)

    # When
    with pytest.raises(CannotDeleteBookingWithReimbursementException) as exception:
        delete_cancelled_booking(venue.id)

    # Then
    assert exception.value.errors["cannotDeleteBookingWithReimbursementException"] == [
        "Réservation non supprimable car elle est liée à un remboursement"
    ]
    assert bookings_models.Booking.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_should_delete_booking_without_reimbursement():
    # Given
    booking = bookings_factories.BookingFactory(status=bookings_models.BookingStatus.CANCELLED)
    venue = booking.venue

    # When
    delete_cancelled_booking(venue.id)

    # Then
    assert bookings_models.Booking.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_should_delete_bookings_without_reimbursement_when_stop_on_exception_is_false():
    # Given
    value_date = datetime.datetime.utcnow()
    booking = bookings_factories.BookingFactory(status=bookings_models.BookingStatus.CANCELLED)
    venue = booking.venue
    booking_with_reimbursement = bookings_factories.BookingFactory(
        stock__offer__venue=venue, status=bookings_models.BookingStatus.CANCELLED
    )
    finance_factories.PricingFactory(
        booking=booking_with_reimbursement, valueDate=value_date, status=PricingStatus.PROCESSED
    )

    # When
    delete_cancelled_booking(venue.id, False)

    # Then
    assert bookings_models.Booking.query.count() == 1
