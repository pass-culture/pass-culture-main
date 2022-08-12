import logging

from pcapi.core.bookings.exceptions import CannotDeleteBookingWithReimbursementException
import pcapi.core.bookings.models as bookings_models
from pcapi.core.finance.repository import has_reimbursement
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_cancelled_booking(venue_id: int, stop_on_exception: bool = True) -> None:
    booking_to_delete = bookings_models.Booking.query.filter(
        bookings_models.Booking.venueId == venue_id,
        bookings_models.Booking.status == bookings_models.BookingStatus.CANCELLED,
    ).all()
    logger.info("%s bookings to delete", len(booking_to_delete))
    for booking in booking_to_delete:
        if has_reimbursement(booking):
            if stop_on_exception:
                db.session.rollback()
                raise CannotDeleteBookingWithReimbursementException()
            logger.info("Can't delete booking #%s : it has at least one linked reimbursement", booking.id)
            continue
        db.session.delete(booking)
        logger.info("Deleting booking #%s", booking.id)
    db.session.commit()
