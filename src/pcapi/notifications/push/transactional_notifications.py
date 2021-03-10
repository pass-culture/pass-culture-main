from dataclasses import dataclass
from enum import Enum
from typing import List
from typing import Optional

from pcapi.core.bookings.models import Booking


class GroupId(Enum):
    CANCEL_BOOKING = "Cancel_booking"


@dataclass
class TransactionalNotificationMessage:
    body: str
    title: Optional[str] = None


@dataclass
class TransactionalNotificationData:
    group_id: str  # Name of the campaign, useful for analytics purpose
    user_ids: List[int]
    message: TransactionalNotificationMessage


def get_notification_data_on_booking_cancellation(bookings: List[Booking]) -> Optional[TransactionalNotificationData]:
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
