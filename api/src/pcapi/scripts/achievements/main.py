import logging

from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only

from pcapi.core.achievements.api import ACHIEVEMENT_NAME_TO_SUBCATEGORY_IDS
from pcapi.core.achievements.api import _get_booking_achievement
from pcapi.core.achievements.models import Achievement
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

SUBCATEGORIES_WITH_ACHIEVEMENT = [
    subcategory_id
    for subcategory_ids in ACHIEVEMENT_NAME_TO_SUBCATEGORY_IDS.values()
    for subcategory_id in subcategory_ids
]
BATCH_SIZE = 2000


def unlock_existing_achievements() -> None:
    last_user_id = 6154339
    has_next_beneficiaries = True

    while has_next_beneficiaries:
        with transaction():
            beneficiaries = _get_beneficiaries(last_user_id, BATCH_SIZE)

            booking_with_achievements = _get_achievement_bookings(beneficiaries)
            _unlock_achievements(booking_with_achievements)

        has_next_beneficiaries = len(beneficiaries) == BATCH_SIZE
        if has_next_beneficiaries:
            last_user_id = beneficiaries[-1].id
            logger.info("Unlocked achievements up to last_user_id = %s", last_user_id)
        elif beneficiaries:
            last_user_id = beneficiaries[-1].id

    logger.info("Finished unlocking achievements up to last_user_id = %s", last_user_id)


def _get_beneficiaries(from_user_id: int, batch_size: int) -> list[User]:
    return (
        db.session.query(User)
        .filter(User.id > from_user_id, User.is_beneficiary.is_(True))
        .options(load_only(User.id))
        .order_by(User.id)
        .limit(batch_size)
        .all()
    )


def _get_achievement_bookings(beneficiaries: list[User]) -> list[Booking]:
    booking_with_achievements_query = (
        db.session.query(Booking)
        .distinct(Booking.userId, Offer.subcategoryId)  # sorting by dateUsed gets the first unlock for each achievement
        .join(Booking.stock)
        .join(Stock.offer)
        .filter(
            Booking.userId.in_([beneficiary.id for beneficiary in beneficiaries]),
            Booking.is_used_or_reimbursed.is_(True),
            Offer.subcategoryId.in_(SUBCATEGORIES_WITH_ACHIEVEMENT),
        )
        .options(joinedload(Booking.user).load_only().selectinload(User.achievements).load_only(Achievement.name))
        .options(contains_eager(Booking.stock).load_only().contains_eager(Stock.offer).load_only(Offer.subcategoryId))
        .options(load_only(Booking.dateUsed))
        .order_by(Booking.userId, Offer.subcategoryId, Booking.dateUsed.nulls_last())
    )
    return booking_with_achievements_query.all()


def _unlock_achievements(bookings: list[Booking]):
    """
    Copied from core.achievements.api without the flushing, to allow for bulk inserts
    """
    for booking in bookings:
        achievement_name = _get_booking_achievement(booking)
        if not achievement_name:
            continue

        previously_unlocked_achievement_names = [
            unlocked_achievement.name for unlocked_achievement in booking.user.achievements
        ]
        if achievement_name in previously_unlocked_achievement_names:
            continue

        achievement = Achievement(
            user=booking.user, booking=booking, name=achievement_name, unlockedDate=booking.dateUsed
        )
        db.session.add(achievement)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    unlock_existing_achievements()
