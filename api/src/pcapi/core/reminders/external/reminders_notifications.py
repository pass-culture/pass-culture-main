import logging

from pcapi.core.external.batch import track_offer_added_to_reminders_event
from pcapi.core.offers.models import Offer
from pcapi.core.offers.repository import exclude_offers_from_inactive_venue_provider
from pcapi.core.offers.repository import get_offers_by_publication_date
from pcapi.core.reminders.repository import get_users_with_reminders


logger = logging.getLogger(__name__)


def notify_users_for_future_offers_activations() -> None:
    query = get_offers_by_publication_date()
    query = exclude_offers_from_inactive_venue_provider(query)

    for offer in query.all():
        notify_users_future_offer_activated(offer=offer)


def notify_users_future_offer_activated(offer: Offer) -> None:
    """
    Find and notify users who activated a reminder for an offer coming soon.
    """
    user_ids = get_users_with_reminders(offer.id)
    if not user_ids:
        logger.warning("No users found", extra={"future_offer": offer.id})
        return

    try:
        track_offer_added_to_reminders_event(user_ids, offer)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "Failed to register track_offer_added_to_reminders_event for offer %d",
            offer.id,
            extra={"offer": offer.id, "users": user_ids},
        )
