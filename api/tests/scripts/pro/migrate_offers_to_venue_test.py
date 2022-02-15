import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.scripts.pro.migrate_offers_to_venue import migrate_offers_to_venue


@pytest.mark.usefixtures("db_session")
def test_migrate_offers_to_venue():
    # Given
    source_venue = VenueFactory()
    BookingFactory(venueId=source_venue.id, offererId=source_venue.managingOfferer.id, stock__offer__venue=source_venue)
    BookingFactory(venueId=source_venue.id, offererId=source_venue.managingOfferer.id, stock__offer__venue=source_venue)
    target_venue = VenueFactory()
    BookingFactory(venueId=target_venue.id, offererId=target_venue.managingOfferer.id, stock__offer__venue=target_venue)

    # When
    migrate_offers_to_venue(source_venue_id=source_venue.id, target_venue_id=target_venue.id)

    # Then
    # don't loose anything
    assert Offer.query.count() == 3
    assert Booking.query.count() == 3
    assert Venue.query.count() == 2
    # Offers and bookings have been migrated
    assert Offer.query.filter(Offer.venueId == target_venue.id).count() == 3
    assert Booking.query.filter(Booking.venueId == target_venue.id).count() == 3
    assert Booking.query.filter(Booking.offererId == target_venue.managingOfferer.id).count() == 3
    # There is anything left in source venue
    assert Offer.query.filter(Offer.venueId == source_venue.id).count() == 0
    assert Booking.query.filter(Booking.venueId == source_venue.id).count() == 0
    assert Booking.query.filter(Booking.offererId == source_venue.managingOfferer.id).count() == 0


@pytest.mark.usefixtures("db_session")
def test_migrate_offers_to_venue_delete_source_venue():
    # Given
    source_venue = VenueFactory()
    target_venue = VenueFactory()

    # When
    migrate_offers_to_venue(source_venue_id=source_venue.id, target_venue_id=target_venue.id, delete_source_venue=True)

    # Then
    assert Venue.query.count() == 1
    assert db.session.query(Venue.query.filter(Venue.id == target_venue.id).exists()).scalar()
