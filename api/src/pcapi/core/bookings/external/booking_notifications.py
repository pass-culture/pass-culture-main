from datetime import date
from datetime import datetime
from datetime import time
import logging

from pcapi import settings
from pcapi.core.bookings.exceptions import BookingIsExpired
from pcapi.core.bookings.repository import get_soon_expiring_bookings
from pcapi.core.offers.repository import find_today_event_stock_ids_metropolitan_france
from pcapi.notifications.push.transactional_notifications import (
    get_soon_expiring_bookings_with_offers_notification_data,
)
from pcapi.tasks import batch_tasks
from pcapi.workers.push_notification_job import send_today_stock_notification


logger = logging.getLogger(__name__)


def send_today_events_notifications_metropolitan_france() -> None:
    """
    Find bookings (grouped by stocks) that occur today in metropolitan
    France but not the morning (11h UTC -> 12h/13h local time), and
    send notification to all the user to remind them of the event.
    """
    today_min = datetime.combine(date.today(), time(hour=11))
    stock_ids = find_today_event_stock_ids_metropolitan_france(today_min)

    for stock_id in stock_ids:
        send_today_stock_notification.delay(stock_id)


def notify_users_bookings_not_retrieved() -> None:
    """
    Find soon expiring bookings that will expire in exactly N days and
    send a notification to each user.
    """
    bookings = get_soon_expiring_bookings(settings.SOON_EXPIRING_BOOKINGS_DAYS_BEFORE_EXPIRATION)
    for booking in bookings:
        try:
            notification_data = get_soon_expiring_bookings_with_offers_notification_data(booking)
            batch_tasks.send_transactional_notification_task.delay(notification_data)
        except BookingIsExpired:
            logger.exception("Booking %d is expired", booking.id, extra={"booking": booking.id, "user": booking.userId})
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "Failed to register send_transactional_notification_task for booking %d",
                booking.id,
                extra={"booking": booking.id, "user": booking.userId},
            )
