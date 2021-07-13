from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models.db import db


@dataclass
class UserUpdateData:
    user_id: str
    attributes: dict


BATCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_user_attributes(user: User) -> dict:
    from pcapi.core.users.api import get_domains_credit

    credit = get_domains_credit(user)
    return {
        "u.credit": int(credit.all.remaining * 100) if credit else 0,
        "u.departement_code": user.departementCode,
        "date(u.date_of_birth)": _format_date(user.dateOfBirth),
        "u.postal_code": user.postalCode,
        "date(u.date_created)": _format_date(user.dateCreated),
        "u.marketing_push_subscription": user.get_notification_subscriptions().marketing_push,
        "u.is_beneficiary": user.isBeneficiary,
        "date(u.deposit_expiration_date)": _format_date(user.deposit_expiration_date),
    }


def get_user_booking_attributes(user: User) -> dict:
    from pcapi.core.users.api import get_domains_credit

    user_bookings = (
        Booking.query.options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .load_only(
                Offer.type,
                Offer.url,
            )
        )
        .filter_by(userId=user.id)
        .order_by(db.desc(Booking.dateCreated))
        .all()
    )

    credit = get_domains_credit(user, [booking for booking in user_bookings if not booking.isCancelled])
    last_booking_date = user_bookings[0].dateCreated if user_bookings else None
    booking_categories = list(set(booking.stock.offer.type for booking in user_bookings))

    attributes = {
        "date(u.last_booking_date)": _format_date(last_booking_date),
        "u.credit": int(credit.all.remaining * 100) if credit else 0,
    }

    # A Batch tag can't be an empty list, otherwise the API returns an error
    if booking_categories:
        attributes["ut.booking_categories"] = booking_categories

    return attributes


def _format_date(date: datetime) -> Optional[str]:
    return date.strftime(BATCH_DATETIME_FORMAT) if date else None
