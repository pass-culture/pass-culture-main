import logging

from pydantic import BaseModel as BaseModelV2

import pcapi.core.bookings.api as bookings_api
import pcapi.core.offers.models as offers_models
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.batch.api import send_transactional_notification
from pcapi.core.external.batch.transactional_notifications import get_bookings_cancellation_notification_data
from pcapi.core.external.batch.transactional_notifications import get_offer_notification_data
from pcapi.core.external.batch.transactional_notifications import get_today_stock_booking_notification_data
from pcapi.models import db


logger = logging.getLogger(__name__)


class SendCancelBookingNotificationPayload(BaseModelV2):
    bookings_ids: list[int]


@celery_async_task(
    name="tasks.batch.priority.send_cancel_booking_notification", model=SendCancelBookingNotificationPayload
)
def send_cancel_booking_notification(payload: SendCancelBookingNotificationPayload) -> None:
    notification_data = get_bookings_cancellation_notification_data(payload.bookings_ids)
    if notification_data:
        send_transactional_notification(notification_data)


class SendTodayStockNotificationPayload(BaseModelV2):
    stock_id: int


@celery_async_task(name="tasks.batch.priority.send_today_stock_notification", model=SendTodayStockNotificationPayload)
def send_today_stock_notification(payload: SendTodayStockNotificationPayload) -> None:
    """
    Send a notification to all bookings linked to a stock.
    """
    offer = (
        db.session.query(offers_models.Offer)
        .join(offers_models.Offer.stocks)
        .filter(offers_models.Stock.id == payload.stock_id)
        .one()
    )
    bookings = bookings_api.get_individual_bookings_from_stock(payload.stock_id)

    for booking in bookings:
        notification_data = get_today_stock_booking_notification_data(booking, offer)
        if notification_data:
            send_transactional_notification(notification_data)


class SendOfferLinkByPushPayload(BaseModelV2):
    user_id: int
    offer_id: int


@celery_async_task(name="tasks.batch.priority.send_offer_link_by_push", model=SendOfferLinkByPushPayload)
def send_offer_link_by_push_task(payload: SendOfferLinkByPushPayload) -> None:
    offer = db.session.query(offers_models.Offer).filter_by(id=payload.offer_id).one()
    notification_data = get_offer_notification_data(payload.user_id, offer)
    send_transactional_notification(notification_data)
