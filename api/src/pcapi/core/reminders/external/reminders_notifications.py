import logging

from pcapi.core.external.batch import send_users_reminders_for_offer
from pcapi.core.offers.models import Offer
from pcapi.core.reminders.repository import delete_offer_reminders_on_offer
from pcapi.core.reminders.repository import get_user_ids_with_reminders


logger = logging.getLogger(__name__)


def notify_users_offer_is_bookable(offer: Offer) -> None:
    user_ids = get_user_ids_with_reminders(offer.id)
    if not user_ids:
        logger.debug("[Offer bookable] No users to notify", extra={"offerId": offer.id})
        return

    logger.debug("[Offer bookable] Users to notify", extra={"offerId": offer.id, "user_ids": user_ids})

    send_users_reminders_for_offer(user_ids, offer)

    delete_offer_reminders_on_offer(offer.id)
