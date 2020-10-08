from pcapi.domain.booking.booking import Booking
from pcapi.domain.booking.booking_repository import BookingRepository
from pcapi.domain.services.notification.notification_service import NotificationService
from pcapi.utils.mailing import send_raw_email


class CancelABooking:
    def __init__(self,
                 booking_repository: BookingRepository,
                 notification_service: NotificationService):
        self.notification_service = notification_service
        self.booking_repository = booking_repository

    def execute(self, booking_id: int, beneficiary_id: int) -> Booking:
        booking = self.booking_repository.find_booking_by_id_and_beneficiary_id(
            booking_id=booking_id,
            beneficiary_id=beneficiary_id
        )
        booking.cancel()

        cancelled_booking = self.booking_repository.save(booking)
        self.notification_service.send_booking_cancellation_emails_to_user_and_offerer(
            booking=cancelled_booking,
            is_offerer_cancellation=False,
            is_user_cancellation=True,
            send_email=send_raw_email
        )
        return cancelled_booking
