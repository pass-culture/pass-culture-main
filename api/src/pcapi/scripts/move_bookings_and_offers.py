import typing

import sqlalchemy as sa

from pcapi.core.bookings.models import Booking
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


IDS = typing.Collection[int]


class ProcessedBooking(Exception):
    pass


def move_bookings_and_their_offers(
    venue_id_src: int, venue_id_dst: int, provider_id: int, dry_run: bool = True
) -> tuple[IDS, IDS]:
    """Move USED BUT NOT REIMBURSED bookings from a venue to another one."""

    # Fetch source and target venues to get information from them: their name and offerer id.
    src_venue = Venue.query.get(venue_id_src)
    dst_venue = Venue.query.get(venue_id_dst)
    ignored_bookings = set()
    booking_ids = set()
    cloned_offers = set()

    offerer_id_dst = dst_venue.managingOffererId

    # get bookings
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
                # raise ProcessedBooking(f"booking {booking.id} is already {current_pricing.status}")
                ignored_bookings.add(booking)
                continue

        booking.venueId = venue_id_dst
        booking.offererId = offerer_id_dst
        booking_ids.add(booking.id)

        if not dry_run:
            db.session.add(booking)

    # delete pricings
    pricings_to_delete = finance_models.Pricing.query.filter(
        finance_models.Pricing.bookingId.in_(booking_ids),
        finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
    ).all()

    pricing_ids = [pricing.id for pricing in pricings_to_delete]
    print(f"{len(pricing_ids)} pricings to delete")

    pricing_lines = finance_models.PricingLine.query.filter(finance_models.PricingLine.pricingId.in_(pricing_ids)).all()
    print(f"{len(pricing_lines)} pricing lines to delete")

    if not dry_run:
        finance_models.PricingLine.query.filter(finance_models.PricingLine.pricingId.in_(pricing_ids)).delete(
            synchronize_session=False
        )
        finance_models.Pricing.query.filter(
            finance_models.Pricing.bookingId.in_(booking_ids),
            finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
        ).delete(synchronize_session=False)

    # update offers (venue and idAtProvider)
    ignored_stocks_ids = {ignored_booking.stockId for ignored_booking in ignored_bookings}
    ignored_offers_ids = {ignored_booking.stock.offerId for ignored_booking in ignored_bookings}

    # pylint: disable=comparison-with-callable
    offers = Offer.query.filter(Offer.venueId == venue_id_src).filter(Offer.lastProviderId == provider_id).all()
    # pylint: disable=comparison-with-callable
    stocks = (
        Stock.query.join(Offer).filter(Offer.venueId == venue_id_src).filter(Offer.lastProviderId == provider_id).all()
    )

    for offer in offers:
        if offer.id in ignored_offers_ids:
            offer = clone_offer(offer)
            cloned_offers.add(offer)

        offer.venueId = venue_id_dst
        offer.idAtProvider = offer.idAtProvider.replace(f"%{venue_id_src}%", f"%{venue_id_dst}%")

        if not dry_run:
            db.session.add(offer)

    for stock in stocks:
        if stock.id in ignored_stocks_ids:
            continue

        stock.idAtProviders = stock.idAtProviders.replace(f"%{venue_id_src}%", f"%{venue_id_dst}%")
        if stock.offerId in ignored_offers_ids:
            for cloned_offer in cloned_offers:
                if cloned_offer.idAtProvider in stock.idAtProviders:
                    stock.offer = cloned_offer
                    break

                raise Exception(  # pylint: disable=broad-exception-raised
                    "Not found cloned offer to be associated to stock"
                )

        if not dry_run:
            db.session.add(stock)

    if dry_run:
        db.session.rollback()

        print(
            (
                f"{len(bookings)} bookings, {len(stocks) - len(ignored_stocks_ids)} / {len(stocks)} stocks and {len(offers) - len(ignored_offers_ids)} / {len(offers)} offers would have been moved from venue '{src_venue.name}'"
                f"{len(cloned_offers)} cloned offers"
                f"({venue_id_src} - attached to offerer {src_venue.managingOffererId}) "
                f"to venue '{dst_venue.name}' ({venue_id_dst} - attached to offerer {dst_venue.managingOffererId})."
            )
        )
    else:
        db.session.commit()
        print(
            (
                f"{len(bookings)} bookings, {len(stocks) - len(ignored_stocks_ids)} / {len(stocks)} stocks and {len(offers) - len(ignored_offers_ids)} / {len(offers)} offers have been moved from venue '{src_venue.name}'"
                f"{len(cloned_offers)} cloned offers"
                f"({venue_id_src} - attached to offerer {src_venue.managingOffererId}) "
                f"to venue '{dst_venue.name}' ({venue_id_dst} - attached to offerer {dst_venue.managingOffererId})."
            )
        )
    moved_bookings_ids = {booking.id for booking in bookings}
    moved_offers_ids = {offer.id for offer in offers}
    return moved_bookings_ids, moved_offers_ids


def clone_offer(offer: Offer) -> Offer:
    return Offer(
        audioDisabilityCompliant=offer.audioDisabilityCompliant,
        bookingContact=offer.bookingContact,
        bookingEmail=offer.bookingEmail,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        externalTicketOfficeUrl=offer.externalTicketOfficeUrl,
        extraData=offer.extraData,
        idAtProvider=offer.idAtProvider,
        isActive=True,
        isDuo=offer.isDuo,
        isNational=offer.isNational,
        mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
        motorDisabilityCompliant=offer.motorDisabilityCompliant,
        lastProviderId=offer.lastProviderId,
        subcategoryId=offer.subcategoryId,
        name=offer.name,
        url=offer.url,
        validation=OfferValidationStatus.APPROVED,
        venueId=offer.venueId,
        visualDisabilityCompliant=offer.visualDisabilityCompliant,
        withdrawalDelay=offer.withdrawalDelay,
        withdrawalDetails=offer.withdrawalDetails,
        withdrawalType=offer.withdrawalType,
    )
