import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.scripts.move_bookings_and_offers import ProcessedBooking
from pcapi.scripts.move_bookings_and_offers import move_bookings_and_theirs_offers


pytestmark = pytest.mark.usefixtures("db_session")


def test_move_bookings_and_theirs_offers():
    src_venue = offerers_factories.VenueFactory()
    dst_venue = offerers_factories.VenueFactory()

    offerers_factories.VenuePricingPointLinkFactory(venue=src_venue, pricingPoint=src_venue)
    offerers_factories.VenuePricingPointLinkFactory(venue=dst_venue, pricingPoint=dst_venue)

    bookings = bookings_factories.UsedBookingFactory.create_batch(3, venue=src_venue, stock__offer__venue=src_venue)
    booking_ids = [booking.id for booking in bookings]

    for booking in bookings:
        finance_factories.PricingFactory(booking=booking)

    move_bookings_and_theirs_offers(booking_ids, src_venue.id, dst_venue.id)

    bookings = Booking.query.filter(Booking.id.in_(booking_ids))

    assert {booking.venueId for booking in bookings} == {dst_venue.id}
    assert {booking.offererId for booking in bookings} == {dst_venue.managingOffererId}

    offers = [booking.stock.offer for booking in bookings]
    assert {offer.venueId for offer in offers} == {dst_venue.id}

    pricing_point_ids = {
        pricing.pricingPointId
        for booking in bookings
        for pricing in booking.pricings
        if pricing.status == finance_models.PricingStatus.VALIDATED
    }

    assert pricing_point_ids == {dst_venue.id}


def test_move_bookings_and_theirs_offers_with_processed_bookings():
    src_venue = offerers_factories.VenueFactory()
    dst_venue = offerers_factories.VenueFactory()

    offerers_factories.VenuePricingPointLinkFactory(venue=src_venue, pricingPoint=src_venue)
    offerers_factories.VenuePricingPointLinkFactory(venue=dst_venue, pricingPoint=dst_venue)

    bookings = bookings_factories.UsedBookingFactory.create_batch(3, venue=src_venue, stock__offer__venue=src_venue)
    booking_ids = [booking.id for booking in bookings]

    for booking in bookings:
        finance_factories.PricingFactory(booking=booking, status=finance_models.PricingStatus.PROCESSED)

    with pytest.raises(ProcessedBooking):
        move_bookings_and_theirs_offers(booking_ids, src_venue.id, dst_venue.id)
