import logging

import pcapi.core.bookings.api as bookings_api
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import Offer
from pcapi.notifications.push import send_transactional_notification
from pcapi.notifications.push.transactional_notifications import get_bookings_cancellation_notification_data
from pcapi.notifications.push.transactional_notifications import get_offer_notification_data
from pcapi.notifications.push.transactional_notifications import get_today_stock_booking_notification_data
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


@job(worker.default_queue)
def send_cancel_booking_notification(bookings_ids: list[int]) -> None:
    notification_data = get_bookings_cancellation_notification_data(bookings_ids)
    if notification_data:
        send_transactional_notification(notification_data)


@job(worker.default_queue)
def send_today_stock_notification(stock_id: int) -> None:
    """
    Send a notification to all bookings linked to a stock.
    """
    offer = offer = (
        offers_models.Offer.query.join(offers_models.Offer.stocks).filter(offers_models.Stock.id == stock_id).one()
    )
    bookings = bookings_api.get_individual_bookings_from_stock(stock_id)

    for booking in bookings:
        notification_data = get_today_stock_booking_notification_data(booking, offer)
        if notification_data:
            send_transactional_notification(notification_data)


@job(worker.default_queue)
def send_offer_link_by_push_job(user_id: int, offer_id: int) -> None:
    offer = Offer.query.get(offer_id)
    notification_data = get_offer_notification_data(user_id, offer)
    send_transactional_notification(notification_data)
