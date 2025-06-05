from sqlalchemy.orm import joinedload

from pcapi.core.offers.models import Offer
from pcapi.core.reminders.models import OfferReminder
from pcapi.core.users.models import User
from pcapi.models import db


def get_reminders(user: User) -> list[OfferReminder]:
    return (
        db.session.query(OfferReminder)
        .filter(OfferReminder.userId == user.id)
        .options(joinedload(OfferReminder.offer).load_only(Offer.id))
        .all()
    )


def get_offer_reminder(user_id: int, offer_id: int) -> OfferReminder | None:
    return (
        db.session.query(OfferReminder)
        .filter(
            OfferReminder.offerId == offer_id,
            OfferReminder.userId == user_id,
        )
        .one_or_none()
    )


def create_offer_reminder(user: User, offer: Offer) -> OfferReminder:
    reminder = OfferReminder(userId=user.id, offerId=offer.id)

    db.session.add(reminder)
    db.session.flush()

    return reminder
