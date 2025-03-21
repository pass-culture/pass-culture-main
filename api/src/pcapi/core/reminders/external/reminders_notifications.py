import logging

from pcapi.core.offers.models import Offer
from pcapi.core.offers.repository import exclude_offers_from_inactive_venue_provider
from pcapi.core.offers.repository import get_offers_by_publication_date
from pcapi.core.reminders.repository import get_users_with_reminders
from pcapi.notifications.push.transactional_notifications import get_future_offer_activated_notification_data
from pcapi.tasks import batch_tasks


logger = logging.getLogger(__name__)


def notify_users_for_future_offers_activations() -> None:
    query = get_offers_by_publication_date()
    query = exclude_offers_from_inactive_venue_provider(query)

    for offer in query.all():
        notify_users_future_offer_activated(offer=offer)


def notify_users_future_offer_activated(offer: Offer) -> None:
    """
    Find and notify users who activated a reminder for a future offer.
    """

    user_ids = get_users_with_reminders(offer.id)
    if not user_ids:
        logger.warning("No users found", extra={"future_offer": offer.id})
        return

    try:
        notification_data = get_future_offer_activated_notification_data(
            user_ids, offer_name=offer.name, offer_id=offer.id
        )
        batch_tasks.send_transactional_notification_task.delay(notification_data)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "Failed to register send_transactional_notification_task for offer %d",
            offer.id,
            extra={"offer": offer.id, "users": user_ids},
        )
