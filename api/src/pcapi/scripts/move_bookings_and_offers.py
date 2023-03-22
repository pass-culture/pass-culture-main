import typing

import sqlalchemy as sa

from pcapi.core.bookings.models import Booking
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.models import db


IDS = typing.Collection[int]


class ProcessedBooking(Exception):
    pass


def move_bookings_and_theirs_offers(
    booking_ids: IDS, venue_id_src: int, venue_id_dst: int, dry_run: bool = True
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
        Booking.query.filter(Booking.id.in_(booking_ids))
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

        finance_api.cancel_pricing(booking, finance_models.PricingLogReason.PRICING_POINT_CHANGED)
        finance_api.price_booking(booking)

        if not dry_run:
            db.session.add(booking)

    # step 2: update their offers (venue only - offers are not linked to
    # and offerer directly)
    offer_ids = {booking.stock.offerId for booking in bookings}
    offers = Offer.query.filter(Offer.id.in_(offer_ids)).all()

    for offer in offers:
        offer.venueId = venue_id_dst

        if not dry_run:
            db.session.add(offer)

    if dry_run:
        db.session.rollback()

        print(
            (
                f"{len(bookings)} bookings and {len(offers)} offers would have been moved from venue '{src_venue.name}'"
                f"({venue_id_src} - attached to offerer {src_venue.managingOffererId}) "
                f"to venue '{dst_venue.name}' ({venue_id_dst} - attached to offerer {dst_venue.managingOffererId})."
            )
        )
    else:
        db.session.commit()

        print(
            (
                f"{len(bookings)} bookings and {len(offers)} offers have been moved from venue '{src_venue.name}'"
                f"({venue_id_src} - attached to offerer {src_venue.managingOffererId}) "
                f"to venue '{dst_venue.name}' ({venue_id_dst} - attached to offerer {dst_venue.managingOffererId})."
            )
        )

    booking_ids = {booking.id for booking in bookings}
    return booking_ids, offer_ids
