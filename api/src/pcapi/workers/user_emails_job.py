import logging

from pcapi.core.bookings.models import Booking
from pcapi.core.mails.transactional.bookings.booking_cancellation import (
    send_booking_cancellation_emails_to_user_and_offerer,
)
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


@job(worker.default_queue)
def send_booking_cancellation_emails_to_user_and_offerer_job(booking_id: int) -> None:
    booking = Booking.query.get(booking_id)
    if not booking:
        logger.error("Booking with id:%s not found", booking_id)
        return
    if not send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason):
        logger.warning(
            "Could not send booking cancellation emails",
            extra={"booking": booking.id},
        )
