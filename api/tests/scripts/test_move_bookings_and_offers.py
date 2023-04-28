import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.scripts.move_bookings_and_offers import ProcessedBooking
from pcapi.scripts.move_bookings_and_offers import move_bookings_and_theirs_offers


pytestmark = pytest.mark.usefixtures("db_session")


def test_move_bookings_and_theirs_offers():
    cgr_provider = get_provider_by_local_class("CGRStocks")

    src_venue = offerers_factories.VenueFactory()
    dst_venue = offerers_factories.VenueFactory()

    offerers_factories.VenuePricingPointLinkFactory(venue=src_venue, pricingPoint=src_venue)
    offerers_factories.VenuePricingPointLinkFactory(venue=dst_venue, pricingPoint=dst_venue)

    offer = offers_factories.OfferFactory(
        idAtProvider=f"1234%{src_venue.id}%CGR", lastProviderId=cgr_provider.id, venue=src_venue
    )
    stock = offers_factories.StockFactory(
        idAtProviders=f"1234%{src_venue.id}%CGR#5678", lastProviderId=cgr_provider.id, offer=offer
    )

    bookings = bookings_factories.UsedBookingFactory.create_batch(3, venue=src_venue, stock=stock)

    booking_ids = [booking.id for booking in bookings]

    for booking in bookings:
        finance_factories.PricingFactory(booking=booking)

    move_bookings_and_theirs_offers(src_venue.id, dst_venue.id, cgr_provider.id, dry_run=False)

    bookings = Booking.query.filter(Booking.id.in_(booking_ids)).all()

    assert {booking.venueId for booking in bookings} == {dst_venue.id}
    assert {booking.offererId for booking in bookings} == {dst_venue.managingOffererId}

    offer = Offer.query.one()
    assert offer.venueId == dst_venue.id
    assert offer.idAtProvider == f"1234%{dst_venue.id}%CGR"

    stocks = Stock.query.all()
    assert {stock.idAtProviders for stock in stocks} == {f"1234%{dst_venue.id}%CGR#5678"}

    pricing_point_ids = {
        pricing.pricingPointId
        for booking in bookings
        for pricing in booking.pricings
        if pricing.status == finance_models.PricingStatus.VALIDATED
    }

    assert pricing_point_ids == {dst_venue.id}


def test_move_bookings_and_theirs_offers_with_processed_bookings():
    cgr_provider = get_provider_by_local_class("CGRStocks")

    src_venue = offerers_factories.VenueFactory()
    dst_venue = offerers_factories.VenueFactory()

    offerers_factories.VenuePricingPointLinkFactory(venue=src_venue, pricingPoint=src_venue)
    offerers_factories.VenuePricingPointLinkFactory(venue=dst_venue, pricingPoint=dst_venue)

    offer = offers_factories.OfferFactory(
        idAtProvider=f"1234%{src_venue.id}%CGR", lastProviderId=cgr_provider.id, venue=src_venue
    )
    stock = offers_factories.StockFactory(
        idAtProviders=f"1234%{src_venue.id}%CGR#5678", lastProviderId=cgr_provider.id, offer=offer
    )

    bookings = bookings_factories.UsedBookingFactory.create_batch(3, venue=src_venue, stock=stock)

    for booking in bookings:
        finance_factories.PricingFactory(booking=booking, status=finance_models.PricingStatus.PROCESSED)

    with pytest.raises(ProcessedBooking):
        move_bookings_and_theirs_offers(src_venue.id, dst_venue.id, cgr_provider.id, dry_run=False)
