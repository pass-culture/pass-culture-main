import logging

from pcapi.core.bookings import api as bookings_api
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
    bookings = bookings_api.get_bookings_with_offers(booking_ids)
    for booking in bookings:
        try:
            notification_data = get_unretrieved_bookings_with_offers_notification_data(booking)
            send_transactional_notification_delayed(notification_data)
        except TypeError:
            logger.error(
                "booking without an expiration date: could build notification data", extra={"booking": booking.id}
            )
