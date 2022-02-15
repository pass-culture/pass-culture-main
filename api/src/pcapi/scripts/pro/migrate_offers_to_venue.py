import logging

from pcapi.core.bookings.models import Booking
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


logger = logging.getLogger(__name__)


def migrate_offers_to_venue(source_venue_id: int, target_venue_id: int, delete_source_venue: bool = False) -> None:
    source_venue = Venue.query.filter(Venue.id == source_venue_id).one()
    target_venue = Venue.query.filter(Venue.id == target_venue_id).one()

    source_bookings = Booking.query.filter(Booking.venueId == source_venue.id).all()
    for booking in source_bookings:
        booking.venueId = target_venue.id
        booking.offererId = target_venue.managingOfferer.id

    source_offers = Offer.query.filter(Offer.venueId == source_venue.id).all()
    for offer in source_offers:
        offer.venueId = target_venue.id
    db.session.commit()

    if delete_source_venue:
        delete_cascade_venue_by_id(source_venue.id)

    recap_data = {
        "source_venue": source_venue_id,
        "target_venue": target_venue_id,
    }
    logging.info("Migrate offers to venue", extra=recap_data)
