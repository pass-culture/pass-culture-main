import datetime
from itertools import groupby
import logging
from operator import attrgetter

from flask_sqlalchemy import BaseQuery

from pcapi import settings
from pcapi.core.bookings.api import recompute_dnBookedQuantity
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
import pcapi.core.educational.repository as educational_repository
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def handle_expired_bookings() -> None:
    handle_expired_individual_bookings()
    handle_expired_collective_bookings()


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


def cancel_expired_individual_bookings(batch_size: int = 500) -> None:
    logger.info("[cancel_expired_individual_bookings] Start")

    expiring_individual_bookings_query = bookings_repository.find_expiring_individual_bookings_query()
    cancel_expired_bookings(expiring_individual_bookings_query, batch_size)

    logger.info("[cancel_expired_individual_bookings] End")


def cancel_expired_bookings(query: BaseQuery, batch_size: int = 500) -> None:
    updated_total = 0
    expiring_booking_ids = [b[0] for b in query.with_entities(Booking.id).all()]

    logger.info("[cancel_expired_bookings] %d expiring bookings to cancel", len(expiring_booking_ids))

    # we commit here to make sure there is no unexpected objects in SQLA cache before the update,
    # as we use synchronize_session=False
    db.session.commit()

    start_index = 0

    while start_index < len(expiring_booking_ids):
        booking_ids_to_update = expiring_booking_ids[start_index : start_index + batch_size]
        updated = Booking.query.filter(Booking.id.in_(booking_ids_to_update)).update(
            {
                "status": BookingStatus.CANCELLED,
                "cancellationReason": BookingCancellationReasons.EXPIRED,
                "cancellationDate": datetime.datetime.utcnow(),
            },
            synchronize_session=False,
        )
        # Recompute denormalized stock quantity
        stocks_to_recompute = [
            row[0]
            for row in db.session.query(Booking.stockId).filter(Booking.id.in_(booking_ids_to_update)).distinct().all()
        ]
        recompute_dnBookedQuantity(stocks_to_recompute)
        db.session.commit()

        updated_total += updated

        logger.info(
            "[cancel_expired_bookings] %d Bookings have been cancelled in this batch",
            updated,
        )

        start_index += batch_size

    logger.info("[cancel_expired_bookings] %d Bookings have been cancelled", updated_total)


def notify_users_of_expired_individual_bookings(expired_on: datetime.date = None) -> None:
    expired_on = expired_on or datetime.date.today()

    logger.info("[notify_users_of_expired_bookings] Start")
    user_ids = bookings_repository.find_user_ids_with_expired_individual_bookings(expired_on)
    notified_users_str = []
    for user_id in user_ids:
        user = User.query.get(user_id)
        transactional_mails.send_expired_bookings_to_beneficiary_email(
            user,
            [
                individual_booking.booking
                for individual_booking in bookings_repository.get_expired_individual_bookings_for_user(user)
            ],
        )
        notified_users_str.append(user.id)

    logger.info(
        "[notify_users_of_expired_bookings] %d Users have been notified: %s",
        len(notified_users_str),
        notified_users_str,
    )

    logger.info("[notify_users_of_expired_bookings] End")


def notify_offerers_of_expired_individual_bookings(expired_on: datetime.date = None) -> None:
    expired_on = expired_on or datetime.date.today()
    logger.info("[notify_offerers_of_expired_bookings] Start")

    expired_individual_bookings_grouped_by_offerer = {
        offerer: list(individual_bookings)
        for offerer, individual_bookings in groupby(
            bookings_repository.find_expired_individual_bookings_ordered_by_offerer(expired_on),
            attrgetter("booking.offerer"),
        )
    }

    notified_offerers = []

    for offerer, individual_bookings in expired_individual_bookings_grouped_by_offerer.items():
        transactional_mails.send_bookings_expiration_to_pro_email(
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


def notify_offerers_of_expired_collective_bookings() -> None:
    logger.info("[notify_offerers_of_expired_collective_bookings] Start")

    expired_collective_bookings = educational_repository.find_expired_collective_bookings()

    for collective_booking in expired_collective_bookings:
        transactional_mails.send_education_booking_cancellation_by_institution_email(collective_booking)

    logger.info(
        "[notify_offerers_of_expired_collective_bookings] %d Offerers have been notified",
        len(expired_collective_bookings),
    )

    logger.info("[notify_offerers_of_expired_collective_bookings] End")


def handle_expired_collective_bookings() -> None:
    logger.info("[handle_expired_collective_bookings] Start")

    try:
        logger.info("[handle_expired_collective_bookings] STEP 1 : cancel_expired_collective_bookings")
        cancel_expired_collective_bookings()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[handle_expired_collective_bookings] Error in STEP 1 : %s", e)

    try:
        logger.info("[handle_expired_educational_bookings] STEP 2 : notify_offerers_of_expired_individual_bookings()")
        notify_offerers_of_expired_collective_bookings()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[handle_expired_educational_bookings] Error in STEP 2 : %s", e)

    logger.info("[handle_expired_collective_bookings] End")


def cancel_expired_collective_bookings(batch_size: int = 500) -> None:
    logger.info("[cancel_expired_collective_bookings] Start")

    expiring_collective_bookings_query = educational_repository.find_expiring_collective_bookings_query()

    expiring_booking_ids = [b[0] for b in expiring_collective_bookings_query.with_entities(CollectiveBooking.id).all()]

    logger.info("[cancel_expired_bookings] %d expiring bookings to cancel", len(expiring_booking_ids))

    # we commit here to make sure there is no unexpected objects in SQLA cache before the update,
    # as we use synchronize_session=False
    db.session.commit()

    updated_total = 0
    start_index = 0

    while start_index < len(expiring_booking_ids):
        booking_to_update_ids = expiring_booking_ids[start_index : start_index + batch_size]
        updated = CollectiveBooking.query.filter(CollectiveBooking.id.in_(booking_to_update_ids)).update(
            {
                "status": CollectiveBookingStatus.CANCELLED,
                "cancellationReason": CollectiveBookingCancellationReasons.EXPIRED,
                "cancellationDate": datetime.datetime.utcnow(),
            },
            synchronize_session=False,
        )
        db.session.commit()

        logger.info(
            "[cancel_expired_bookings] %d Bookings have been cancelled in this batch",
            updated,
        )

        updated_total += updated
        start_index += batch_size

    logger.info("[cancel_expired_bookings] %d Bookings have been cancelled", updated_total)
    logger.info("[cancel_expired_collective_bookings] End")
