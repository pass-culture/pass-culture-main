import logging

from pcapi.core.external.batch import send_users_reminders_for_offer
from pcapi.core.offers.models import Offer
from pcapi.core.offers.repository import exclude_offers_from_inactive_venue_provider
from pcapi.core.offers.repository import get_offers_by_publication_date
from pcapi.core.reminders.repository import get_user_ids_with_reminders


logger = logging.getLogger(__name__)


def notify_users_for_future_offers_activations() -> None:
    query = get_offers_by_publication_date()
    query = exclude_offers_from_inactive_venue_provider(query)

    for offer in query:
        notify_users_future_offer_activated(offer=offer)


def notify_users_future_offer_activated(offer: Offer) -> None:
    user_ids = get_user_ids_with_reminders(offer.id)
    if not user_ids:
        logger.warning("No users found", extra={"future_offer": offer.id})
        return

    send_users_reminders_for_offer(user_ids, offer)
