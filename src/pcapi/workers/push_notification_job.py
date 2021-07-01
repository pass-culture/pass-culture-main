import logging
from typing import Callable

from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.notifications.push import send_transactional_notification
from pcapi.notifications.push import update_user_attributes
from pcapi.notifications.push.transactional_notifications import get_bookings_cancellation_notification_data
from pcapi.notifications.push.transactional_notifications import get_offer_notification_data
from pcapi.notifications.push.transactional_notifications import get_tomorrow_stock_notification_data
from pcapi.notifications.push.user_attributes_updates import get_user_attributes
from pcapi.notifications.push.user_attributes_updates import get_user_booking_attributes
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


@job(worker.default_queue)
def update_user_attributes_job(user_id: int, *extra_providers: Callable[[User], dict]) -> None:
    user = User.query.get(user_id)
    if not user:
        logger.error("No user with id=%s found to send push attributes updates requests", user_id)
        return

    update_user_attributes(user.id, get_user_attributes(user))


@job(worker.default_queue)
def update_user_bookings_attributes_job(user_id: int) -> None:
    user = User.query.get(user_id)
    if not user:
        logger.error("No user with id=%s found to send push attributes updates requests", user_id)
        return

    update_user_attributes(user.id, get_user_booking_attributes(user))


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
