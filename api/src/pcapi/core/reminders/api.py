from sqlalchemy.orm import joinedload

from pcapi.core.offers.models import FutureOffer
from pcapi.core.offers.models import Offer
from pcapi.core.reminders.models import FutureOfferReminder
from pcapi.core.reminders.models import OfferReminder
from pcapi.core.users.models import User
from pcapi.models import db


def get_reminders(user: User) -> list[FutureOfferReminder]:
    return (
        db.session.query(FutureOfferReminder)
        .filter(FutureOfferReminder.userId == user.id)
        .options(
            joinedload(FutureOfferReminder.futureOffer)
            .load_only(FutureOffer.offerId)
            .joinedload(FutureOffer.offer)
            .load_only(Offer.id)
        )
    ).all()


def get_future_offer_reminder(user_id: int, future_offer_id: int) -> FutureOfferReminder | None:
    return (
        db.session.query(FutureOfferReminder)
        .filter(
            FutureOfferReminder.futureOfferId == future_offer_id,
            FutureOfferReminder.userId == user_id,
        )
        .one_or_none()
    )


def create_future_offer_reminder(user: User, future_offer: FutureOffer) -> FutureOfferReminder:
    reminder = FutureOfferReminder(userId=user.id, futureOfferId=future_offer.id)

    db.session.add(reminder)
    db.session.flush()

    return reminder


def delete_future_offer_reminder(user: User, reminder_id: int) -> None:
    reminder = db.session.query(FutureOfferReminder).filter_by(id=reminder_id, user=user).first_or_404()

    db.session.delete(reminder)


def create_offer_reminder(user: User, offer: Offer) -> OfferReminder:
    reminder = OfferReminder(userId=user.id, offerId=offer.id)

    db.session.add(reminder)
    db.session.flush()

    return reminder


def delete_offer_reminder(user: User, offer_id: int) -> None:
    reminder = db.session.query(OfferReminder).filter_by(offerId=offer_id, user=user).one_or_none()

    if reminder:
        db.session.delete(reminder)
