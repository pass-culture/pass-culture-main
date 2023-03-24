from pcapi.analytics.amplitude.backends import amplitude_connector
from pcapi.core.bookings import models as bookings_models
from pcapi.tasks import amplitude_tasks


def track_book_offer_event(booking: bookings_models.Booking) -> None:
    _track_booking_event(booking, amplitude_connector.AmplitudeEventType.OFFER_BOOKED)


def track_cancel_booking_event(
    booking: bookings_models.Booking, reason: bookings_models.BookingCancellationReasons
) -> None:
    _track_booking_event(booking, amplitude_connector.AmplitudeEventType.BOOKING_CANCELLED, reason)


def track_mark_as_used_event(booking: bookings_models.Booking) -> None:
    _track_booking_event(booking, amplitude_connector.AmplitudeEventType.BOOKING_USED)


def _track_booking_event(
    booking: bookings_models.Booking,
    event_name: amplitude_connector.AmplitudeEventType,
    reason: bookings_models.BookingCancellationReasons | None = None,
) -> None:
    event_properties = _get_booking_event_properties(booking)
    if reason:
        event_properties["reason"] = reason.value
    amplitude_tasks.track_event.delay(
        amplitude_tasks.TrackAmplitudeEventRequest(
            user_id=booking.userId,
            event_name=event_name,
            event_properties=event_properties,
        )
    )


def _get_booking_event_properties(booking: bookings_models.Booking) -> dict:
    return {
        "offer_id": booking.stock.offerId,
        "price": float(booking.total_amount),
        "booking_id": booking.id,
        "category": booking.stock.offer.category.id,
        "subcategory": booking.stock.offer.subcategoryId,
    }
