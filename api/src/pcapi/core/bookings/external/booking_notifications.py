from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import logging
import typing

from pcapi import settings
from pcapi.core.bookings.exceptions import BookingIsExpired
from pcapi.core.bookings.repository import get_soon_expiring_bookings
import pcapi.core.offers.repository as offers_repository
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
    France but not the morning (11h UTC -> 12h/13h local time) and
    send notifications to all the users.
    """
    today_min, today_max = _setup_today_min_max(utc_mean_offset=1)
    stock_ids = find_today_event_stock_ids_metropolitan_france(today_min, today_max)

    if not stock_ids:
        logger.warning("No stock found", extra={"today_min": today_min, "departments": today_max})
        return

    for stock_id in stock_ids:
        try:
            send_today_stock_notification.delay(stock_id)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Could not send today stock notification", extra={"stock": stock_id})


def send_today_events_notifications_overseas(utc_mean_offset: int, departments: typing.Iterable[str]) -> None:
    """
    Find bookings (grouped by stocks) that occur today in overseas
    french departments but not the morning (11h UTC), and send
    notifications to all the users.

    Example:
        to target bookings from la Réunion,
        send_today_events_notifications_overseas(5, ["974"])
    """
    today_min, today_max = _setup_today_min_max(utc_mean_offset)
    stock_ids = offers_repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments)

    if not stock_ids:
        logger.warning(
            "No stock found",
            extra={
                "today_min": today_min,
                "today_max": today_max,
                "utc_mean_offset": utc_mean_offset,
                "departments": departments,
            },
        )
        return

    for stock_id in stock_ids:
        try:
            send_today_stock_notification.delay(stock_id)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Could not send today stock notification", extra={"stock": stock_id})


def _setup_today_min_max(utc_mean_offset: int, start_utc_hour: int = 13) -> tuple[datetime, datetime]:
    """
    Build datetime time slots: the UTC datetimes that corresponds to the
    expected local ones.

    Example:
        * local time is UTC+5, and the target is 13h->23h59,
          the corresponding UTC time slots is 8h->18h59;

          _setup_today_min_max(5)
          returns datetime(<today>, 8, 0), datetime(<today>, 18, 59)

        * local time is UTC-6, and the target is still 13h->23h59,
          the corresponding UTC time slots is 19h(today)->5h59(tomorrow);

          _setup_today_min_max(-6)
          returns datetime(<today>, 19, 0), datetime(<tomorrow>, 5, 59)
    """
    today_min_base = datetime.combine(date.today(), time(hour=start_utc_hour))
    today_max_base = datetime.combine(date.today(), time(hour=23, minute=59))

    today_min = today_min_base - timedelta(hours=utc_mean_offset)
    today_max = today_max_base - timedelta(hours=utc_mean_offset)

    return today_min, today_max


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
