import logging

from rq.decorators import job

from pcapi.core.bookings.models import Booking
from pcapi.domain.user_emails import send_booking_cancellation_emails_to_user_and_offerer
from pcapi.utils.mailing import MailServiceException
from pcapi.workers import worker
from pcapi.workers.decorators import job_context
from pcapi.workers.decorators import log_job


logger = logging.getLogger(__name__)


@job(worker.default_queue, connection=worker.conn)
@job_context
@log_job
def send_booking_cancellation_emails_to_user_and_offerer_job(booking_id: int) -> None:
    booking = Booking.query.get(booking_id)
    if not booking:
        logger.error("Booking with id:%s not found", booking_id)
    try:
        send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)
    except MailServiceException as error:
        logger.exception("Could not send booking=%s cancellation emails: %s", booking.id, error)
