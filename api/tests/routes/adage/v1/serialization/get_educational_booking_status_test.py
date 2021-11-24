import pytest

from pcapi.core.bookings import factories as educational_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.routes.adage.v1.serialization.prebooking import get_educational_booking_status


@pytest.mark.usefixtures("db_session")
class GetEducationalBookingStatusTest:
    def test_get_educational_booking_status_returns_used(self):
        # Given
        booking = educational_factories.EducationalBookingFactory(
            status=bookings_models.BookingStatus.USED,
            educationalBooking__status=educational_models.EducationalBookingStatus.REFUSED,
        )

        # When
        status = get_educational_booking_status(booking.educationalBooking)

        # Then
        assert status == "USED"

    def test_get_educational_booking_status_returns_used_when_reimbursed(self):
        # Given
        booking = educational_factories.EducationalBookingFactory(
            status=bookings_models.BookingStatus.REIMBURSED,
            educationalBooking__status=educational_models.EducationalBookingStatus.REFUSED,
        )

        # When
        status = get_educational_booking_status(booking.educationalBooking)

        # Then
        assert status == "USED"

    def test_get_educational_booking_status_returns_educational_status(self):
        # Given
        booking = educational_factories.EducationalBookingFactory(
            status=bookings_models.BookingStatus.PENDING,
            educationalBooking__status=educational_models.EducationalBookingStatus.REFUSED,
        )

        # When
        status = get_educational_booking_status(booking.educationalBooking)

        # Then
        assert status == "REFUSED"

    def test_get_educational_booking_status_returns_booking_status(self):
        # Given
        booking = educational_factories.EducationalBookingFactory(
            status=bookings_models.BookingStatus.PENDING,
            educationalBooking__status=None,
        )

        # When
        status = get_educational_booking_status(booking.educationalBooking)

        # Then
        assert status == "PENDING"
