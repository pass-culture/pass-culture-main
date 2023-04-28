import typing

import sqlalchemy as sa

from pcapi.core.bookings.models import Booking
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.models import db


IDS = typing.Collection[int]


class ProcessedBooking(Exception):
    pass


def move_bookings_and_theirs_offers(
    venue_id_src: int,
    venue_id_dst: int,
    provider_id: int,
    dry_run: bool = True,
) -> tuple[IDS, IDS]:
    """
    Move USED BUT NOT REIMBURSED bookings from a venue to another one.
    """
    # Fetch source and target venues to get information from them: their
    # name and offerer id.
    src_venue = Venue.query.get(venue_id_src)
    dst_venue = Venue.query.get(venue_id_dst)

    offerer_id_dst = dst_venue.managingOffererId

    # step 1: update bookings (venue and offerer)
    bookings = (
        Booking.query.join(Stock)
        .filter(Booking.venueId == venue_id_src)
        .filter(Stock.lastProviderId == provider_id)
        .options(sa.orm.joinedload(Booking.stock).joinedload(Stock.offer))
        .options(sa.orm.joinedload(Booking.venue).joinedload(Venue.pricing_point_links))
        .options(sa.orm.joinedload(Booking.pricings))
        .all()
    )

    for booking in bookings:
        # Ensure that no booking has already been reimbursed
        pricings = sorted(booking.pricings, key=lambda x: x.creationDate, reverse=True) if booking.pricings else []
        if pricings:
            current_pricing = pricings[0]
            if current_pricing.status in (
                finance_models.PricingStatus.PROCESSED,
                finance_models.PricingStatus.INVOICED,
            ):
                raise ProcessedBooking(f"booking {booking.id} is already {current_pricing.status}")

        booking.venueId = venue_id_dst
        booking.offererId = offerer_id_dst

        if not dry_run:
            db.session.add(booking)

    # step 4: delete pricings and recompute new pricings
    booking_ids = [booking.id for booking in bookings]
    pricings_to_delete = finance_models.Pricing.query.filter(
        finance_models.Pricing.bookingId.in_(booking_ids),
        finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
    ).all()

    pricing_ids = [pricing.id for pricing in pricings_to_delete]
    print(f"{len(pricing_ids)} pricings to delete")

    pricing_lines = finance_models.PricingLine.query.filter(
        finance_models.PricingLine.pricingId.in_(pricing_ids),
    ).all()

    print(f"{len(pricing_lines)} pricing lines to delete")

    if not dry_run:
        finance_models.PricingLine.query.filter(
            finance_models.PricingLine.pricingId.in_(pricing_ids),
        ).delete(synchronize_session=False)

        finance_models.Pricing.query.filter(
            finance_models.Pricing.bookingId.in_(booking_ids),
            finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
        ).delete(synchronize_session=False)

    # step 3: update their offers (venue and idAtProvider)
    offers = Offer.query.filter(Offer.venueId == venue_id_src).filter(Offer.lastProviderId == provider_id).all()
    stocks = (
        Stock.query.join(Offer).filter(Offer.venueId == venue_id_src).filter(Offer.lastProviderId == provider_id).all()
    )

    for offer in offers:
        offer.venueId = venue_id_dst
        offer.idAtProvider = offer.idAtProvider.replace(f"%{venue_id_src}%", f"%{venue_id_dst}%")

        if not dry_run:
            db.session.add(offer)

    # step 4: update their stocks (only idAtProviders)
    for stock in stocks:
        stock.idAtProviders = stock.idAtProviders.replace(f"%{venue_id_src}%", f"%{venue_id_dst}%")

        if not dry_run:
            db.session.add(stock)

    if dry_run:
        db.session.rollback()

        print(
            (
                f"{len(bookings)} bookings, {len(stocks)} stocks and {len(offers)} offers would have been moved from venue '{src_venue.name}'"
                f"({venue_id_src} - attached to offerer {src_venue.managingOffererId}) "
                f"to venue '{dst_venue.name}' ({venue_id_dst} - attached to offerer {dst_venue.managingOffererId})."
            )
        )
    else:
        db.session.commit()

        print(
            (
                f"{len(bookings)} bookings, {len(stocks)} stocks and {len(offers)} offers have been moved from venue '{src_venue.name}'"
                f"({venue_id_src} - attached to offerer {src_venue.managingOffererId}) "
                f"to venue '{dst_venue.name}' ({venue_id_dst} - attached to offerer {dst_venue.managingOffererId})."
            )
        )

    booking_ids = {booking.id for booking in bookings}
    offer_ids = {offer.id for offer in offers}
    return booking_ids, offer_ids


move_bookings_and_theirs_offers(36944, 15497, 1073, True)
