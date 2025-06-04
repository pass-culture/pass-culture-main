import logging

from pcapi.core.external.batch import send_users_reminders_for_offer
from pcapi.core.offers.models import Offer
from pcapi.core.reminders.repository import delete_offer_reminders_on_offer
from pcapi.core.reminders.repository import delete_reminders_on_offer
from pcapi.core.reminders.repository import get_user_ids_with_reminders


logger = logging.getLogger(__name__)


def notify_users_future_offer_activated(offer: Offer) -> None:
    user_ids = get_user_ids_with_reminders(offer.id)
    if not user_ids:
        logger.warning("No users found", extra={"future_offer": offer.id})
        return

    send_users_reminders_for_offer(user_ids, offer)

    delete_reminders_on_offer(offer.id)
    # NOTE: (tcoudray-pass, 04/06/2025)
    # On effectue une double écriture avant de remplacer
    # `FutureOfferReminder` par `OfferReminder`
    delete_offer_reminders_on_offer(offer.id)
