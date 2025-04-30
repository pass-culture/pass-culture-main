from sqlalchemy.orm import joinedload

from pcapi.core.offers.models import FutureOffer
from pcapi.core.offers.models import Offer
from pcapi.core.reminders.models import FutureOfferReminder
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.routes.native.v1.serialization.reminder import PostReminderRequest


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


def create_reminder(user: User, reminder_body: PostReminderRequest) -> FutureOfferReminder:
    query = db.session.query(FutureOffer).filter(FutureOffer.offerId == reminder_body.offer_id)
    future_offer = query.first_or_404()

    existing_reminder = (
        db.session.query(FutureOfferReminder)
        .filter(FutureOfferReminder.futureOfferId == future_offer.id, FutureOfferReminder.userId == user.id)
        .one_or_none()
    )

    if existing_reminder:
        return existing_reminder

    reminder = FutureOfferReminder(
        userId=user.id,
        futureOfferId=future_offer.id,
    )

    db.session.add(reminder)
    db.session.flush()

    return reminder


def delete_reminder(user: User, reminder_id: int) -> None:
    reminder = db.session.query(FutureOfferReminder).filter_by(id=reminder_id, user=user).first_or_404()

    db.session.delete(reminder)
