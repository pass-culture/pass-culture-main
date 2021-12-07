from datetime import datetime
from datetime import timedelta
import logging

from pcapi.core.bookings import api as bookings_repository
from pcapi.core.offers.models import Offer
from pcapi.notifications.push import send_transactional_notification
from pcapi.notifications.push import send_transactional_notification_delayed
from pcapi.notifications.push.transactional_notifications import get_bookings_cancellation_notification_data
from pcapi.notifications.push.transactional_notifications import get_offer_notification_data
from pcapi.notifications.push.transactional_notifications import get_tomorrow_stock_notification_data
from pcapi.notifications.push.transactional_notifications import get_unretrieved_bookings_with_offers_notification_data
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


@job(worker.default_queue)
def send_cancel_booking_notification(bookings_ids: list[int]) -> None:
    notification_data = get_bookings_cancellation_notification_data(bookings_ids)
    if notification_data:
        send_transactional_notification(notification_data)


@job(worker.default_queue)
def send_tomorrow_stock_notification(stock_id: int) -> None:
    notification_data = get_tomorrow_stock_notification_data(stock_id)
    if notification_data:
        send_transactional_notification(notification_data)


@job(worker.default_queue)
def send_offer_link_by_push_job(user_id: int, offer_id: int) -> None:
    offer = Offer.query.get(offer_id)
    notification_data = get_offer_notification_data(user_id, offer)
    send_transactional_notification(notification_data)


@job(worker.default_queue)
def send_unretrieved_bookings_from_offer_notification_job(booking_ids: list[int]) -> None:
    """
    Send a notification to each of the unexpired bookings.
    Filter bookings that will expire too soon to avoid a useless
    notification.
    """
    expires_at_min = datetime.utcnow() - timedelta(hours=1)
    bookings = bookings_repository.get_unexpired_bookings(booking_ids, expires_at_min)

    for booking in bookings:
        notification_data = get_unretrieved_bookings_with_offers_notification_data(booking)

        try:
            send_transactional_notification_delayed(notification_data)
        except TypeError:
            logger.error(
                "booking without an expiration date: could not build notification data", extra={"booking": booking.id}
            )
