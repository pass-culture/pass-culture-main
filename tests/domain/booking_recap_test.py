from domain.booking_recap.booking_recap import compute_booking_recap_status, BookingRecapStatus
from models import Booking


class ComputeBookingRecapStatusTest:
    def test_should_return_booked_status_when_booking_is_not_cancelled_nor_used(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.isCancelled = False

        # When
        booking_recap_status = compute_booking_recap_status(booking)

        # Then
        assert booking_recap_status == BookingRecapStatus.booked

    def test_should_return_validated_status_when_booking_is_used_and_not_cancelled(self):
        # Given
        booking = Booking()
        booking.isUsed = True
        booking.isCancelled = False

        # When
        booking_recap_status = compute_booking_recap_status(booking)

        # Then
        assert booking_recap_status == BookingRecapStatus.validated

    def test_should_return_cancelled_status_when_booking_is_cancelled_but_not_used(self):
        # Given
        booking = Booking()
        booking.isUsed = False
        booking.isCancelled = True

        # When
        booking_recap_status = compute_booking_recap_status(booking)

        # Then
        assert booking_recap_status == BookingRecapStatus.cancelled

    def test_should_return_cancelled_status_when_booking_is_cancelled_and_used(self):
        # Given
        booking = Booking()
        booking.isUsed = True
        booking.isCancelled = True

        # When
        booking_recap_status = compute_booking_recap_status(booking)

        # Then
        assert booking_recap_status == BookingRecapStatus.cancelled
