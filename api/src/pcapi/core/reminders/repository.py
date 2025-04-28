from pcapi.core.offers.models import FutureOffer
from pcapi.core.reminders.models import FutureOfferReminder
from pcapi.models import db


def get_user_ids_with_reminders(offer_id: int) -> list[int]:
    future_offer_reminders_query = (
        db.session.query(FutureOfferReminder)
        .join(FutureOfferReminder.futureOffer)
        .filter(FutureOffer.offerId == offer_id)
    )

    return [reminder.userId for reminder in future_offer_reminders_query]


def delete_reminders_on_offer(offer_id: int) -> None:
    future_offer_reminders_query = (
        db.session.query(FutureOfferReminder.id)
        .join(FutureOfferReminder.futureOffer)
        .filter(FutureOffer.offerId == offer_id)
    )
    db.session.query(FutureOfferReminder).filter(FutureOfferReminder.id.in_(future_offer_reminders_query)).delete(
        synchronize_session=False
    )
