from pcapi.core.reminders.models import OfferReminder
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


def get_user_ids_with_reminders(offer_id: int) -> list[int]:
    offer_reminders_query = db.session.query(OfferReminder).filter(OfferReminder.offerId == offer_id)

    return [reminder.userId for reminder in offer_reminders_query]


@atomic()
def delete_offer_reminders_on_offer(offer_id: int) -> None:
    db.session.query(OfferReminder).filter(OfferReminder.offerId == offer_id).delete(synchronize_session=False)
