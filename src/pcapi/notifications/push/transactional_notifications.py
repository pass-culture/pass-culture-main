from dataclasses import dataclass
from enum import Enum
from typing import Optional

from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Stock


class GroupId(Enum):
    CANCEL_BOOKING = "Cancel_booking"
    TOMORROW_STOCK = "Tomorrow_stock"


@dataclass
class TransactionalNotificationMessage:
    body: str
    title: Optional[str] = None


@dataclass
class TransactionalNotificationData:
    group_id: str  # Name of the campaign, useful for analytics purpose
    user_ids: list[int]
    message: TransactionalNotificationMessage


def get_bookings_cancellation_notification_data(booking_ids: list[int]) -> Optional[TransactionalNotificationData]:
    bookings = Booking.query.filter(Booking.id.in_(booking_ids))

    if not bookings:
        return None

    cancelled_object = (
        "commande" if bookings[0].stock.offer.isDigital or bookings[0].stock.offer.isThing else "réservation"
    )
    return TransactionalNotificationData(
        group_id=GroupId.CANCEL_BOOKING.value,
        user_ids=[booking.userId for booking in bookings],
        message=TransactionalNotificationMessage(
            title=f"{cancelled_object.capitalize()} annulée",
            body=f"""Ta {cancelled_object} "{bookings[0].stock.offer.name}" a été annulée par l'offreur.""",
        ),
    )


def get_tomorrow_stock_notification_data(stock_id: int) -> Optional[TransactionalNotificationData]:
    stock = Stock.query.filter_by(id=stock_id).join(Booking).join(Stock.offer).one()
    bookings = [booking for booking in stock.bookings if not booking.isCancelled]

    if not bookings:
        return None

    return TransactionalNotificationData(
        group_id=GroupId.TOMORROW_STOCK.value,
        user_ids=[booking.userId for booking in bookings],
        message=TransactionalNotificationMessage(
            title=f"{stock.offer.name}, c'est demain !",
            body="Retrouve les détails de la réservation sur l’appli Pass Culture",
        ),
    )
