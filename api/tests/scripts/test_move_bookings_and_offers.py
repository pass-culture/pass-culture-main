import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.scripts.move_bookings_and_offers import move_bookings_and_their_offers


pytestmark = pytest.mark.usefixtures("db_session")


def test_move_bookings_and_their_offers():
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

    move_bookings_and_their_offers(src_venue.id, dst_venue.id, cgr_provider.id, dry_run=False)

    bookings = Booking.query.filter(Booking.id.in_(booking_ids)).all()

    assert {booking.venueId for booking in bookings} == {dst_venue.id}
    assert {booking.offererId for booking in bookings} == {dst_venue.managingOffererId}

    offer = Offer.query.one()
    assert offer.venueId == dst_venue.id
    assert offer.idAtProvider == f"1234%{dst_venue.id}%CGR"

    stocks = Stock.query.all()
    assert {stock.idAtProviders for stock in stocks} == {f"1234%{dst_venue.id}%CGR#5678"}

    pricings = finance_models.Pricing.query.all()
    assert not pricings


def test_move_bookings_and_theirs_offers_with_processed_bookings():
    cgr_provider = get_provider_by_local_class("CGRStocks")

    src_venue = offerers_factories.VenueFactory()
    dst_venue = offerers_factories.VenueFactory()

    offerers_factories.VenuePricingPointLinkFactory(venue=src_venue, pricingPoint=src_venue)
    offerers_factories.VenuePricingPointLinkFactory(venue=dst_venue, pricingPoint=dst_venue)

    offer = offers_factories.OfferFactory(
        idAtProvider=f"1234%{src_venue.id}%CGR", lastProviderId=cgr_provider.id, venue=src_venue
    )
    offer_with_processed_booking = offers_factories.OfferFactory(
        idAtProvider=f"444%{src_venue.id}%CGR", lastProviderId=cgr_provider.id, venue=src_venue
    )
    stock = offers_factories.StockFactory(
        idAtProviders=f"1234%{src_venue.id}%CGR#5678", lastProviderId=cgr_provider.id, offer=offer
    )
    stock_with_processed_booking = offers_factories.StockFactory(
        idAtProviders=f"444%{src_venue.id}%CGR#5555", lastProviderId=cgr_provider.id, offer=offer_with_processed_booking
    )
    stock_with_not_processed_booking = offers_factories.StockFactory(
        idAtProviders=f"444%{src_venue.id}%CGR#6666", lastProviderId=cgr_provider.id, offer=offer_with_processed_booking
    )

    bookings = bookings_factories.UsedBookingFactory.create_batch(3, venue=src_venue, stock=stock)
    not_processed_booking = bookings_factories.UsedBookingFactory(
        venue=src_venue, stock=stock_with_not_processed_booking
    )
    processed_booking = bookings_factories.ReimbursedBookingFactory(venue=src_venue, stock=stock_with_processed_booking)
    finance_factories.PricingFactory(booking=processed_booking, status=finance_models.PricingStatus.PROCESSED)

    move_bookings_and_their_offers(src_venue.id, dst_venue.id, cgr_provider.id, dry_run=False)

    assert Offer.query.count() == 3

    assert {booking.venueId for booking in bookings} == {dst_venue.id}
    assert {booking.offererId for booking in bookings} == {dst_venue.managingOffererId}

    assert not_processed_booking.venueId == dst_venue.id
    assert not_processed_booking.offererId == dst_venue.managingOffererId

    assert stock_with_not_processed_booking.offer.venueId == dst_venue.id
    assert stock_with_processed_booking.offer.venueId == src_venue.id
    assert stock_with_processed_booking.offer.name == stock_with_not_processed_booking.offer.name
    assert stock_with_processed_booking.offer.description == stock_with_not_processed_booking.offer.description

    assert processed_booking.venueId == src_venue.id
    assert processed_booking.offererId == src_venue.managingOffererId

    assert offer.venueId == dst_venue.id
    assert offer.idAtProvider == f"1234%{dst_venue.id}%CGR"

    assert offer_with_processed_booking.venueId == src_venue.id
    assert offer_with_processed_booking.idAtProvider == f"444%{src_venue.id}%CGR"

    assert stock.idAtProviders == f"1234%{dst_venue.id}%CGR#5678"
    assert stock_with_processed_booking.idAtProviders == f"444%{src_venue.id}%CGR#5555"

    pricing = finance_models.Pricing.query.one()
    assert pricing.status == finance_models.PricingStatus.PROCESSED
    assert pricing.booking == processed_booking
