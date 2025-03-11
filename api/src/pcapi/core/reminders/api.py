from pcapi.core.offers.models import FutureOffer
from pcapi.core.reminders.models import FutureOfferReminder
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.routes.native.v1.serialization.reminder import PostReminderRequest


def create_reminder(user: User, reminder: PostReminderRequest) -> FutureOfferReminder:

    query = db.session.query(FutureOffer).filter(FutureOffer.offerId == reminder.offer_id)
    future_offer = query.first_or_404()

    existing_reminder = (
        db.session.query(FutureOfferReminder).filter(FutureOfferReminder.futureOfferId == future_offer.id).one_or_none()
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
