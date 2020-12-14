import datetime
from itertools import groupby
from operator import attrgetter

from pcapi.core.bookings import conf
import pcapi.core.bookings.repository as bookings_repository
from pcapi.utils.logger import logger


def notify_users_of_expired_bookings(expired_on: datetime.date = None) -> None:
    """
    This script will be scheduled to begin after CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE, but can be called before that
    date manually in order to check the number of emails that would be sent.
    """
    expired_on = expired_on or datetime.date.today()

    logger.info("[notify_users_of_expired_bookings] Start")
    expired_bookings_ordered_by_user = bookings_repository.find_expired_bookings_ordered_by_user(expired_on)

    expired_bookings_grouped_by_user = dict()
    for user, booking in groupby(expired_bookings_ordered_by_user, attrgetter("user")):
        expired_bookings_grouped_by_user[user] = list(booking)

    is_after_start_date = datetime.datetime.utcnow() >= conf.CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE
    notified_users = []

    if is_after_start_date:
        for user, _bookings in expired_bookings_grouped_by_user.items():
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
    """
    This script will be scheduled to begin after CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE, but can be called before that
    date manually in order to check the number of emails that would be sent.
    """
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
        for offerer, _bookings in expired_bookings_grouped_by_offerer.items():
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
