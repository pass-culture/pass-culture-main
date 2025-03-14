import logging

from pcapi.core.offers.models import Offer
from pcapi.core.reminders.models import FutureOfferReminder
from pcapi.models import db
from pcapi.notifications.push.transactional_notifications import get_future_offer_activated_notification_data
from pcapi.tasks import batch_tasks


logger = logging.getLogger(__name__)


def _get_users_with_reminders_from_future_offer(future_offer_id: int) -> list[int]:
    future_offer_reminders = (
        db.session.query(FutureOfferReminder).filter(FutureOfferReminder.futureOfferId == future_offer_id).all()
    )

    return [reminder.userId for reminder in future_offer_reminders]


def notify_users_future_offer_activated(future_offer_id: int) -> None:
    """
    Find and notify users who activated a reminder for a future offer.
    """

    user_ids = _get_users_with_reminders_from_future_offer(future_offer_id)

    offer: Offer = db.session.query(Offer).get(Offer.futureOffer.id == future_offer_id)

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
