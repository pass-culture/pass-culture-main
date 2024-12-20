from typing import Generator
import logging

from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only

from pcapi.core.achievements.api import ACHIEVEMENT_NAME_TO_SUBCATEGORY_IDS
from pcapi.core.achievements.api import unlock_achievement
from pcapi.core.achievements.models import Achievement
from pcapi.core.bookings.models import Booking
from pcapi.core.logging import log_elapsed
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.repository import atomic


logger = logging.getLogger(__name__)

SUBCATEGORIES_WITH_ACHIEVEMENT = [
    subcategory_id
    for subcategory_ids in ACHIEVEMENT_NAME_TO_SUBCATEGORY_IDS.values()
    for subcategory_id in subcategory_ids
]
BATCH_SIZE = 1000


def unlock_achievements() -> None:
    last_user_id = 0
    has_next_beneficiaries = True

    while has_next_beneficiaries:
        with atomic():
            beneficiaries = _get_beneficiaries(last_user_id)

            booking_with_achievements = _get_achievement_bookings(beneficiaries)
            for booking in booking_with_achievements:
                achievement = unlock_achievement(booking)
                if achievement and booking.dateUsed:
                    achievement.unlockDate = booking.dateUsed
                    db.session.flush()

            has_next_beneficiaries = bool(beneficiaries)
            if has_next_beneficiaries:
                last_user_id = beneficiaries[-1].id
                logger.info(f"Unlocked achievements up to {last_user_id = }")


def _get_beneficiaries(from_user_id: int) -> list[User]:
    return (
        db.session.query(User)
        .filter(User.id > from_user_id, User.is_beneficiary.is_(True))
        .order_by(User.id)
        .options(load_only(User.id))
        .limit(BATCH_SIZE)
        .all()
    )


def _get_achievement_bookings(beneficiaries: list[User]) -> list[Booking]:
    beneficiary_ids = [beneficiary.id for beneficiary in beneficiaries]
    booking_with_achievements_query = (
        db.session.query(Booking)
        .distinct(Booking.userId, Offer.subcategoryId)  # sorting by dateUsed gets the first unlock for each achievement
        .join(Booking.stock)
        .join(Stock.offer)
        .filter(
            Booking.userId.in_(beneficiary_ids),
            Booking.is_used_or_reimbursed.is_(True),
            Offer.subcategoryId.in_(SUBCATEGORIES_WITH_ACHIEVEMENT),
        )
        .options(
            joinedload(Booking.user).load_only(User.id).selectinload(User.achievements).load_only(Achievement.name)
        )
        .options(
            contains_eager(Booking.stock).load_only(Stock.id).contains_eager(Stock.offer).load_only(Offer.subcategoryId)
        )
        .options(load_only(Booking.id, Booking.userId, Booking.dateUsed))
        .order_by(Booking.userId, Offer.subcategoryId, Booking.dateUsed.nulls_last())
    )
    return booking_with_achievements_query.all()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    unlock_achievements()
