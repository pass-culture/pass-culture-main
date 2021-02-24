from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock


def count_active_bookings_for_venue(venue_id: int) -> int:
    return (
        Booking.query.join(Stock)
        .join(Offer)
        .filter(venue_id == Offer.venueId, Booking.isUsed.is_(False), Booking.isCancelled.is_(False))
        .count()
    )
