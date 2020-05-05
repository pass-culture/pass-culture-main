from domain.booking_recap.booking_recap import compute_booking_recap_status, BookingRecapStatus
from models import Booking
from models.payment_status import TransactionStatus


class ComputeBookingRecapStatusTest:
    class WhenBookingHasNoPaymentsTest:
        def test_should_return_booked_status_when_booking_is_not_cancelled_nor_used(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = False
            booking.paymentStatus = None

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.booked

        def test_should_return_validated_status_when_booking_is_used_and_not_cancelled(self):
            # Given
            booking = Booking()
            booking.isUsed = True
            booking.isCancelled = False
            booking.paymentStatus = None

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.validated

        def test_should_return_cancelled_status_when_booking_is_cancelled_but_not_used(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = True
            booking.paymentStatus = None

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.cancelled

        def test_should_return_cancelled_status_when_booking_is_cancelled_and_used(self):
            # Given
            booking = Booking()
            booking.isUsed = True
            booking.isCancelled = True
            booking.paymentStatus = None

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.cancelled

    class WhenBookingPaymentStatusIsNotSentTest:
        def test_should_return_cancelled_status_when_booking_is_cancelled_and_payment_status_is_pending(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = True
            booking.paymentStatus = TransactionStatus.PENDING

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.cancelled

        def test_should_return_cancelled_status_when_booking_is_cancelled_and_payment_status_is_not_processable(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = True
            booking.paymentStatus = TransactionStatus.NOT_PROCESSABLE

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.cancelled

        def test_should_return_cancelled_status_when_booking_is_cancelled_and_payment_status_is_error(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = True
            booking.paymentStatus = TransactionStatus.ERROR

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.cancelled

        def test_should_return_cancelled_status_when_booking_is_cancelled_and_payment_status_is_retry(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = True
            booking.paymentStatus = TransactionStatus.RETRY

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.cancelled

        def test_should_return_cancelled_status_when_booking_is_cancelled_and_payment_status_is_banned(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = True
            booking.paymentStatus = TransactionStatus.BANNED

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.cancelled

    class WhenBookingPaymentStatusIsSentTest:
        def test_should_return_reimbursed_status_when_booking_is_not_cancelled_nor_used(self):
            # Given
            booking = Booking()
            booking.isUsed = False
            booking.isCancelled = False
            booking.paymentStatus = TransactionStatus.SENT

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.reimbursed

        def test_should_return_reimbursed_status_when_booking_is_used_and_not_cancelled(self):
            # Given
            booking = Booking()
            booking.isUsed = True
            booking.isCancelled = False
            booking.paymentStatus = TransactionStatus.SENT

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.reimbursed

        def test_should_return_reimbursed_status_when_booking_is_used_and_cancelled(self):
            # Given
            booking = Booking()
            booking.isUsed = True
            booking.isCancelled = True
            booking.paymentStatus = TransactionStatus.SENT

            # When
            booking_recap_status = compute_booking_recap_status(booking)

            # Then
            assert booking_recap_status == BookingRecapStatus.reimbursed
