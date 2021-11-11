import logging

from pcapi.core.bookings import models as bookings_models
from pcapi.core.payments import models as payments_models
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def fill_individual_booking_deposit_id(batch_size=1000):
    individual_booking_ids = [
        result[0]
        for result in bookings_models.IndividualBooking.query.with_entities(bookings_models.IndividualBooking.id)
        .filter(bookings_models.IndividualBooking.depositId.is_(None))
        .all()
    ]

    start_index = 0

    while start_index < len(individual_booking_ids):
        print(f"Updating bookings {start_index}/{len(individual_booking_ids)}")
        updated_bookings_count = 0
        individual_bookings = (
            bookings_models.IndividualBooking.query.join(users_models.User)
            .join(
                bookings_models.Booking,
                bookings_models.Booking.individualBookingId == bookings_models.IndividualBooking.id,
            )
            .join(payments_models.Deposit, payments_models.Deposit.userId == users_models.User.id)
            .filter(
                bookings_models.IndividualBooking.id.in_(individual_booking_ids[start_index : start_index + batch_size])
            )
            .all()
        )
        for individual_booking in individual_bookings:
            if individual_booking.user.deposit is None:
                continue
            if individual_booking.booking.dateCreated > individual_booking.user.deposit.expirationDate:
                if individual_booking.booking.amount > 0:
                    logger.warning(
                        "Booking with amount > 0 made after deposit expiration date id=%s",
                        individual_booking.booking.id,
                    )
                continue

            individual_booking.depositId = (
                individual_booking.user.deposit.id if individual_booking.user.deposit else None
            )
            updated_bookings_count += 1
            db.session.add(individual_booking)

        db.session.commit()
        start_index += batch_size

        print(f"Updated {updated_bookings_count} individual bookings")
