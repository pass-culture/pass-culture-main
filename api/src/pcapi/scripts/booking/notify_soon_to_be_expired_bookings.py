import datetime
from itertools import groupby
import logging
from operator import attrgetter

from pcapi import settings
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.mails.transactional as transactional_mails


logger = logging.getLogger(__name__)


def notify_soon_to_be_expired_individual_bookings() -> None:
    logger.info("[notify_soon_to_be_expired_individual_bookings] Start")
    if settings.IS_STAGING:
        logger.info("[handle_expired_individual_bookings] ENV=STAGING: Skipping")
    else:
        notify_users_of_soon_to_be_expired_individual_bookings()
    logger.info("[notify_soon_to_be_expired_individual_bookings] End")


def notify_users_of_soon_to_be_expired_individual_bookings(given_date: datetime.date = None) -> None:
    logger.info("[notify_users_of_soon_to_be_expired_bookings] Start")

    expired_individual_bookings_grouped_by_user = {
        user: list(individual_booking)
        for user, individual_booking in groupby(
            bookings_repository.find_soon_to_be_expiring_individual_bookings_ordered_by_user(given_date),
            attrgetter("user"),
        )
    }

    notified_users = []

    for user, individual_bookings in expired_individual_bookings_grouped_by_user.items():
        transactional_mails.send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary(
            user, [individual_booking.booking for individual_booking in individual_bookings]
        )
        notified_users.append(user)

    logger.info(
        "[notify_users_of_soon_to_be_expired_individual_bookings] %d Users have been notified: %s",
        len(notified_users),
        notified_users,
    )

    logger.info("[notify_users_of_soon_to_be_expired_individual_bookings] End")
