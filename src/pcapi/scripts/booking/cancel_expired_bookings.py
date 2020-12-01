from datetime import datetime

from pcapi.core.bookings import conf
import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.repository import find_expiring_bookings
from pcapi.utils.logger import logger


def cancel_expired_bookings(batch_size: int = 100) -> None:
    """
    This script will be scheduled to begin after CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE, but can be called before that
    date manually in order to check the number of Bookings that would be cancelled/expired
    Note that the batch_size is pretty conservatory, in order to limit the DB locks to the minimum
    """

    logger.info("[cancel_expired_bookings] Start")
    bookings_to_expire = find_expiring_bookings().all()
    is_after_start_date = datetime.utcnow() >= conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE
    cancelled_bookings = []
    errors = []

    if is_after_start_date:
        for batch in range(0, len(bookings_to_expire), batch_size):
            batch_cancelled_bookings, batch_errors = bookings_api.cancel_expired_bookings(
                bookings_to_expire[batch : batch + batch_size],
            )
            cancelled_bookings.extend(batch_cancelled_bookings)
            if batch_errors:
                errors.extend(batch_errors)

        logger.info(
            "%d Bookings have been cancelled: %s",
            len(cancelled_bookings),
            cancelled_bookings,
        )

        if errors:
            logger.exception("Encountered these validation errors: %s", errors)

    else:
        logger.info(
            "%d Bookings would have been cancelled: %s",
            len(bookings_to_expire),
            cancelled_bookings,
        )

    logger.info("[cancel_expired_bookings] End")
