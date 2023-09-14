from enum import Enum

import pcapi.core.bookings.models as bookings_models
from pcapi.core.external_bookings.serialize import ExternalEventBookingRequest


class BookingAction(str, Enum):
    BOOK = "BOOK"
    CANCEL = "CANCEL"


class ExternalApiBookingNotificationRequest(ExternalEventBookingRequest):
    action: BookingAction

    @classmethod
    def build(cls, booking: bookings_models.Booking, action: BookingAction) -> "ExternalApiBookingNotificationRequest":
        return cls(
            action=action,
            **ExternalEventBookingRequest.build_external_booking(booking.stock, booking, booking.user).dict(),
        )
