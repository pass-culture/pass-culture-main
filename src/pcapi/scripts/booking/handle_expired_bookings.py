import datetime
from itertools import groupby
from operator import attrgetter

from pcapi.core.bookings import conf
import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.bookings.repository import find_expiring_bookings
from pcapi.domain.user_emails import send_expired_bookings_recap_email_to_beneficiary
from pcapi.domain.user_emails import send_expired_bookings_recap_email_to_offerer
from pcapi.utils.logger import logger
from pcapi.utils.mailing import send_raw_email


def handle_expired_bookings() -> None:
    logger.info("[handle_expired_bookings] Start")

    try:
        logger.info("[handle_expired_bookings] STEP 1 : cancel_expired_bookings()")
        cancel_expired_bookings()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[handle_expired_bookings] Error in STEP 1 : %s", e)

    try:
        logger.info("[handle_expired_bookings] STEP 2 : notify_users_of_expired_bookings()")
        notify_users_of_expired_bookings()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[handle_expired_bookings] Error in STEP 2 : %s", e)

    try:
        logger.info("[handle_expired_bookings] STEP 3 : notify_offerers_of_expired_bookings()")
        notify_offerers_of_expired_bookings()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[handle_expired_bookings] Error in STEP 3 : %s", e)

    logger.info("[handle_expired_bookings] End")


def cancel_expired_bookings(batch_size: int = 100) -> None:
    logger.info("[cancel_expired_bookings] Start")
    bookings_to_expire = find_expiring_bookings().all()
    is_after_start_date = datetime.datetime.utcnow() >= conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE
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
            logger.exception("[cancel_expired_bookings] Encountered these validation errors: %s", errors)

    else:
        logger.info(
            "%d Bookings would have been selected for cancellation: %s",
            len(bookings_to_expire),
            bookings_to_expire,
        )

    logger.info("[cancel_expired_bookings] End")


def notify_users_of_expired_bookings(expired_on: datetime.date = None) -> None:
    expired_on = expired_on or datetime.date.today()

    logger.info("[notify_users_of_expired_bookings] Start")
    expired_bookings_ordered_by_user = bookings_repository.find_expired_bookings_ordered_by_user(expired_on)

    expired_bookings_grouped_by_user = dict()
    for user, booking in groupby(expired_bookings_ordered_by_user, attrgetter("user")):
        expired_bookings_grouped_by_user[user] = list(booking)

    is_after_start_date = datetime.datetime.utcnow() >= conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE
    notified_users = []

    if is_after_start_date:
        for user, bookings in expired_bookings_grouped_by_user.items():
            send_expired_bookings_recap_email_to_beneficiary(user, bookings, send_raw_email)
            notified_users.append(user)

        logger.info(
            "%d Users have been notified: %s",
            len(notified_users),
            notified_users,
        )

    else:
        logger.info(
            "%d Users would have been notified of expired booking cancellation: %s",
            len(expired_bookings_grouped_by_user),
            expired_bookings_grouped_by_user,
        )

    logger.info("[notify_users_of_expired_bookings] End")


def notify_offerers_of_expired_bookings(expired_on: datetime.date = None) -> None:
    expired_on = expired_on or datetime.date.today()
    logger.info("[notify_offerers_of_expired_bookings] Start")

    expired_bookings_ordered_by_offerer = bookings_repository.find_expired_bookings_ordered_by_offerer(expired_on)
    expired_bookings_grouped_by_offerer = dict()
    for offerer, booking in groupby(
        expired_bookings_ordered_by_offerer, attrgetter("stock.offer.venue.managingOfferer")
    ):
        expired_bookings_grouped_by_offerer[offerer] = list(booking)

    is_after_start_date = datetime.datetime.utcnow() >= conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE
    notified_offerers = []

    if is_after_start_date:
        for offerer, bookings in expired_bookings_grouped_by_offerer.items():
            send_expired_bookings_recap_email_to_offerer(offerer, bookings, send_raw_email)
            notified_offerers.append(offerer)

        logger.info(
            "%d Offerers have been notified: %s",
            len(notified_offerers),
            notified_offerers,
        )

    else:
        logger.info(
            "%d Offerers would have been notified of expired booking cancellation: %s",
            len(expired_bookings_grouped_by_offerer),
            expired_bookings_grouped_by_offerer,
        )

    logger.info("[notify_offerers_of_expired_bookings] End")
