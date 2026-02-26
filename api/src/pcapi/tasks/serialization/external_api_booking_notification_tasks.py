import pcapi.core.bookings.models as bookings_models
from pcapi.core.external_bookings.serialize import ExternalEventBookingRequest
from pcapi.core.providers.tasks import BookingAction


class ExternalApiBookingNotificationRequest(ExternalEventBookingRequest):
    action: BookingAction

    @classmethod
    def build(cls, booking: bookings_models.Booking, action: BookingAction) -> "ExternalApiBookingNotificationRequest":
        return cls(
            action=action,
            **ExternalEventBookingRequest.build_external_booking(booking.stock, booking, booking.user).dict(),
        )
