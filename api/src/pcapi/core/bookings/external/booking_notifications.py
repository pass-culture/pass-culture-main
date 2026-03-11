import logging

from pcapi import settings
from pcapi.core.bookings.exceptions import BookingIsExpired
from pcapi.core.bookings.repository import get_soon_expiring_bookings
from pcapi.core.external.batch.transactional_notifications import (
    get_soon_expiring_bookings_with_offers_notification_data,
)
from pcapi.tasks import batch_tasks as batch_cloud_tasks


logger = logging.getLogger(__name__)


def notify_users_bookings_not_retrieved() -> None:
    """
    Find soon expiring bookings that will expire in exactly N days and
    send a notification to each user.
    """
    bookings = get_soon_expiring_bookings(settings.SOON_EXPIRING_BOOKINGS_DAYS_BEFORE_EXPIRATION)
    for booking in bookings:
        try:
            notification_data = get_soon_expiring_bookings_with_offers_notification_data(booking)
            batch_cloud_tasks.send_transactional_notification_task.delay(notification_data)
        except BookingIsExpired:
            logger.exception("Booking %d is expired", booking.id, extra={"booking": booking.id, "user": booking.userId})
        except Exception:
            logger.exception(
                "Failed to register send_transactional_notification_task for booking %d",
                booking.id,
                extra={"booking": booking.id, "user": booking.userId},
            )
