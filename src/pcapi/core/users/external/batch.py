from datetime import datetime
import logging
from typing import Optional

from pcapi.core.bookings.models import Booking
from pcapi.core.users.models import User
from pcapi.tasks.batch_tasks import UpdateBatchAttributesRequest
from pcapi.tasks.batch_tasks import update_user_attributes_task


logger = logging.getLogger(__name__)


BATCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

# make sure values are in [a-z0-9_] (no uppercase characters, no '-')
TRACKED_PRODUCT_IDS = {3084625: "brut_x"}


def update_user_attributes(user: User, user_bookings: list[Booking]):
    attributes = get_user_attributes(user, user_bookings)
    update_user_attributes_task.delay(UpdateBatchAttributesRequest(user_id=user.id, attributes=attributes))


def get_user_attributes(user: User, user_bookings: list[Booking]) -> dict:
    from pcapi.core.users.api import get_domains_credit

    credit = get_domains_credit(user, [booking for booking in user_bookings if not booking.isCancelled])
    last_booking_date = user_bookings[0].dateCreated if user_bookings else None
    booking_categories = list(set(booking.stock.offer.type for booking in user_bookings))

    attributes = {
        "u.credit": int(credit.all.remaining * 100) if credit else 0,
        "u.departement_code": user.departementCode,
        "date(u.date_of_birth)": _format_date(user.dateOfBirth),
        "u.postal_code": user.postalCode,
        "date(u.date_created)": _format_date(user.dateCreated),
        "u.marketing_push_subscription": user.get_notification_subscriptions().marketing_push,
        "u.is_beneficiary": user.isBeneficiary,
        "date(u.deposit_expiration_date)": _format_date(user.deposit_expiration_date),
        "date(u.last_booking_date)": _format_date(last_booking_date),
    }

    for booking in user_bookings:
        if booking.dateUsed and booking.stock.offer.productId in TRACKED_PRODUCT_IDS:
            attributes[f"date(u.product_{TRACKED_PRODUCT_IDS[booking.stock.offer.productId]}_use)"] = _format_date(
                booking.dateUsed
            )

    # A Batch tag can't be an empty list, otherwise the API returns an error
    if booking_categories:
        attributes["ut.booking_categories"] = booking_categories

    return attributes


def _format_date(date: Optional[datetime]) -> Optional[str]:
    return date.strftime(BATCH_DATETIME_FORMAT) if date else None
