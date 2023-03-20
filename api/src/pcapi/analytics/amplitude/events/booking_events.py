from pcapi.analytics.amplitude.backends import amplitude_connector
from pcapi.tasks import amplitude_tasks


def track_book_offer_event(booking: bookings_models.Booking) -> None:
    amplitude_tasks.track_event.delay(
        amplitude_tasks.TrackAmplitudeEventRequest(
            user_id=booking.userId or 0,
            event_name=amplitude_connector.AmplitudeEventType.OFFER_BOOKED,
            event_properties={
                "offer_id": booking.stock.offerId,
                "price": float(booking.total_amount),
                "booking_id": booking.id,
                "category": booking.stock.offer.category.id,
                "subcategory": booking.stock.offer.subcategoryId,
                # TODO: add offer type (showType, musicType, BookMacroSection, MovieGenre, ...)
                # "offer_type": ???
            },
        )
    )
