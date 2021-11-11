import datetime
from itertools import groupby
import logging
from operator import attrgetter

from sqlalchemy.orm import Query

from pcapi import settings
from pcapi.core.bookings.api import recompute_dnBookedQuantity
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.bookings.repository as bookings_repository
from pcapi.domain.user_emails import send_expired_bookings_recap_email_to_beneficiary
from pcapi.domain.user_emails import send_expired_individual_bookings_recap_email_to_offerer
from pcapi.models import db


logger = logging.getLogger(__name__)


def handle_expired_bookings() -> None:
    handle_expired_individual_bookings()
    handle_expired_educational_bookings()


def handle_expired_educational_bookings() -> None:
    logger.info("[handle_expired_educational_bookings] Start")

    try:
        logger.info("[handle_expired_educational_bookings] STEP 1 : cancel_expired_educational_bookings()")
        cancel_expired_educational_bookings()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[handle_expired_educational_bookings] Error in STEP 1 : %s", e)


def handle_expired_individual_bookings() -> None:
    logger.info("[handle_expired_individual_bookings] Start")

    try:
        logger.info("[handle_expired_individual_bookings] STEP 1 : cancel_expired_individual_bookings()")
        cancel_expired_individual_bookings()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[handle_expired_individual_bookings] Error in STEP 1 : %s", e)
    if settings.IS_STAGING:
        logger.info("[handle_expired_individual_bookings] ENV=STAGING: Skipping Steps 2 and 3")
    else:
        try:
            logger.info("[handle_expired_individual_bookings] STEP 2 : notify_users_of_expired_individual_bookings()")
            notify_users_of_expired_individual_bookings()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("[handle_expired_individual_bookings] Error in STEP 2 : %s", e)

        try:
            logger.info(
                "[handle_expired_individual_bookings] STEP 3 : notify_offerers_of_expired_individual_bookings()"
            )
            notify_offerers_of_expired_individual_bookings()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("[handle_expired_individual_bookings] Error in STEP 3 : %s", e)

    logger.info("[handle_expired_individual_bookings] End")


def cancel_expired_educational_bookings(batch_size: int = 500) -> None:
    logger.info("[cancel_expired_educational_bookings] Start")

    expiring_educational_bookings_query = bookings_repository.find_expiring_educational_bookings_query()
    cancel_expired_bookings(expiring_educational_bookings_query, batch_size)

    logger.info("[cancel_expired_educational_bookings] End")


def cancel_expired_individual_bookings(batch_size: int = 500) -> None:
    logger.info("[cancel_expired_individual_bookings] Start")

    expiring_individual_bookings_query = bookings_repository.find_expiring_individual_bookings_query()
    cancel_expired_bookings(expiring_individual_bookings_query, batch_size)

    logger.info("[cancel_expired_individual_bookings] End")


def cancel_expired_bookings(query: Query, batch_size: int = 500):
    expiring_bookings_count = query.count()
    logger.info("[cancel_expired_bookings] %d expiring bookings to cancel", expiring_bookings_count)
    if expiring_bookings_count == 0:
        return

    updated_total = 0
    expiring_booking_ids = bookings_repository.find_expiring_booking_ids_from_query(query).limit(batch_size).all()
    max_id = expiring_booking_ids[-1][0]

    # we commit here to make sure there is no unexpected objects in SQLA cache before the update,
    # as we use synchronize_session=False
    db.session.commit()

    while expiring_booking_ids:
        updated = (
            Booking.query.filter(Booking.id <= max_id)
            .filter(Booking.id.in_(expiring_booking_ids))
            .update(
                {
                    "isCancelled": True,
                    "status": BookingStatus.CANCELLED,
                    "cancellationReason": BookingCancellationReasons.EXPIRED,
                    "cancellationDate": datetime.datetime.utcnow(),
                },
                synchronize_session=False,
            )
        )
        # Recompute denormalized stock quantity
        stocks_to_recompute = [
            row[0]
            for row in db.session.query(Booking.stockId).filter(Booking.id.in_(expiring_booking_ids)).distinct().all()
        ]
        recompute_dnBookedQuantity(stocks_to_recompute)
        db.session.commit()

        updated_total += updated
        expiring_booking_ids = bookings_repository.find_expiring_booking_ids_from_query(query).limit(batch_size).all()
        if expiring_booking_ids:
            max_id = expiring_booking_ids[-1][0]
        logger.info(
            "[cancel_expired_bookings] %d Bookings have been cancelled in this batch",
            updated,
        )

    logger.info(
        "[cancel_expired_bookings] %d Bookings have been cancelled",
        updated_total,
    )


def notify_users_of_expired_individual_bookings(expired_on: datetime.date = None) -> None:
    expired_on = expired_on or datetime.date.today()

    logger.info("[notify_users_of_expired_bookings] Start")
    expired_individual_bookings_ordered_by_user = bookings_repository.find_expired_individual_bookings_ordered_by_user(
        expired_on
    )

    expired_bookings_grouped_by_user = dict()
    for user, individual_bookings in groupby(expired_individual_bookings_ordered_by_user, attrgetter("user")):
        expired_bookings_grouped_by_user[user] = list(individual_bookings)

    notified_users = []

    for user, individual_bookings in expired_bookings_grouped_by_user.items():
        send_expired_bookings_recap_email_to_beneficiary(
            user, [individual_booking.booking for individual_booking in individual_bookings]
        )
        notified_users.append(user)

    logger.info(
        "[notify_users_of_expired_bookings] %d Users have been notified: %s",
        len(notified_users),
        notified_users,
    )

    logger.info("[notify_users_of_expired_bookings] End")


def notify_offerers_of_expired_individual_bookings(expired_on: datetime.date = None) -> None:
    expired_on = expired_on or datetime.date.today()
    logger.info("[notify_offerers_of_expired_bookings] Start")

    expired_individual_bookings_ordered_by_offerer = (
        bookings_repository.find_expired_individual_bookings_ordered_by_offerer(expired_on)
    )
    expired_individual_bookings_grouped_by_offerer = dict()
    for offerer, individual_bookings in groupby(
        expired_individual_bookings_ordered_by_offerer, attrgetter("booking.offerer")
    ):
        expired_individual_bookings_grouped_by_offerer[offerer] = list(individual_bookings)

    notified_offerers = []

    for offerer, individual_bookings in expired_individual_bookings_grouped_by_offerer.items():
        send_expired_individual_bookings_recap_email_to_offerer(
            offerer,
            [individual_booking.booking for individual_booking in individual_bookings],
        )
        notified_offerers.append(offerer)

    logger.info(
        "[notify_users_of_expired_individual_bookings] %d Offerers have been notified: %s",
        len(notified_offerers),
        notified_offerers,
    )

    logger.info("[notify_offerers_of_expired_individual_bookings] End")
