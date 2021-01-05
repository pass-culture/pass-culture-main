import datetime
from itertools import groupby
from operator import attrgetter

import pcapi.core.bookings.repository as bookings_repository
from pcapi.domain.user_emails import send_soon_to_be_expired_bookings_recap_email_to_beneficiary
from pcapi.utils.logger import logger
from pcapi.utils.mailing import send_raw_email


def notify_soon_to_be_expired_bookings() -> None:
    logger.info("[notify_soon_to_be_expired_bookings] Start")

    notify_users_of_soon_to_be_expired_bookings()

    logger.info("[notify_soon_to_be_expired_bookings] End")


def notify_users_of_soon_to_be_expired_bookings(given_date: datetime.date = None) -> None:
    logger.info("[notify_users_of_soon_to_be_expired_bookings] Start")
    bookings_ordered_by_user = bookings_repository.find_soon_to_be_expiring_booking_ordered_by_user(given_date)

    expired_bookings_grouped_by_user = dict()
    for user, booking in groupby(bookings_ordered_by_user, attrgetter("user")):
        expired_bookings_grouped_by_user[user] = list(booking)

    notified_users = []

    for user, bookings in expired_bookings_grouped_by_user.items():
        send_soon_to_be_expired_bookings_recap_email_to_beneficiary(user, bookings, send_raw_email)
        notified_users.append(user)

    logger.info(
        "[notify_users_of_soon_to_be_expired_bookings] %d Users have been notified: %s",
        len(notified_users),
        notified_users,
    )

    logger.info("[notify_users_of_soon_to_be_expired_bookings] End")
