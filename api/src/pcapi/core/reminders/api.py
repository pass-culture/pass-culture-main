from pcapi.core.offers.models import FutureOffer
from pcapi.core.reminders.models import FutureOfferReminder
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.routes.native.v1.serialization.reminder import PostReminderRequest


def create_reminder(user: User, reminder: PostReminderRequest) -> None:
    future_offer = FutureOffer.query.filter(FutureOffer.offerId == reminder.offer_id).first_or_404()

    existing_reminder = next(
        (
            user_reminder
            for user_reminder in user.future_offer_reminders
            if user_reminder.futureOffer.offerId == reminder.offer_id
        ),
        None,
    )

    if existing_reminder:
        return

    reminder = FutureOfferReminder(
        userId=user.id,
        futureOfferId=future_offer.id,
    )

    db.session.add(reminder)
