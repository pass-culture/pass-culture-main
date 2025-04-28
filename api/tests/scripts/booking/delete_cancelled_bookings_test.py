import pytest

from pcapi.core.bookings.exceptions import CannotDeleteBookingWithReimbursementException
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import PricingStatus
from pcapi.models import db
from pcapi.scripts.booking.delete_cancelled_booking import delete_cancelled_booking


@pytest.mark.usefixtures("db_session")
def test_should_not_delete_booking_with_reimbursement():
    # Given
    pricing = finance_factories.PricingFactory(status=PricingStatus.PROCESSED)
    booking = pricing.booking
    booking.cancel_booking(
        bookings_models.BookingCancellationReasons.FINANCE_INCIDENT,
        cancel_even_if_used=True,
    )
    db.session.flush()

    # When
    with pytest.raises(CannotDeleteBookingWithReimbursementException) as exception:
        delete_cancelled_booking(booking.venueId)

    # Then
    assert exception.value.errors["cannotDeleteBookingWithReimbursementException"] == [
        "Réservation non supprimable car elle est liée à un remboursement"
    ]
    assert db.session.query(bookings_models.Booking).count() == 1


@pytest.mark.usefixtures("db_session")
def test_should_delete_booking_without_reimbursement():
    # Given
    booking = bookings_factories.BookingFactory(status=bookings_models.BookingStatus.CANCELLED)
    venue = booking.venue

    # When
    delete_cancelled_booking(venue.id)

    # Then
    assert db.session.query(bookings_models.Booking).count() == 0


@pytest.mark.usefixtures("db_session")
def test_should_delete_bookings_without_reimbursement_when_stop_on_exception_is_false():
    # Given
    booking = bookings_factories.CancelledBookingFactory()
    venue = booking.venue
    pricing = finance_factories.PricingFactory(
        status=PricingStatus.PROCESSED,
        booking__stock__offer__venue=venue,
    )
    booking_with_reimbursement = pricing.booking
    booking_with_reimbursement.cancel_booking(
        bookings_models.BookingCancellationReasons.FINANCE_INCIDENT,
        cancel_even_if_used=True,
    )
    db.session.flush()

    # When
    delete_cancelled_booking(venue.id, stop_on_exception=False)

    # Then
    assert db.session.query(bookings_models.Booking).one() == booking_with_reimbursement
