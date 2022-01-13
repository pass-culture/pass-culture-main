from pcapi.core import search
from pcapi.core.bookings.api import recompute_dnBookedQuantity
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.models import db
from pcapi.scripts.stock.fully_sync_venue import fully_sync_venue


def migrate_bookings(old_venue_id: int, new_venue_id: int) -> None:
    new_venue = Venue.query.get(new_venue_id)
    updated_stock_count = 0
    offer_moved_count = 0
    for booking in (
        Booking.query.join(Stock, Booking.stock)
        .join(Offer, Stock.offer)
        .filter(Offer.venueId == old_venue_id, Offer.idAtProvider.isnot(None))
    ):
        idAtProvider = booking.stock.offer.idAtProvider
        new_stock = (
            Stock.query.join(Offer, Stock.offer)
            .filter(Offer.venueId == new_venue_id, Offer.idAtProvider == idAtProvider)
            .one_or_none()
        )
        if new_stock:
            booking.stock = new_stock
            db.session.add(booking)
            db.session.flush()
            updated_stock_count += 1
        else:
            offer = booking.stock.offer
            offer.venueId = new_venue_id
            offer.idAtProviders = "%s@%s" % (offer.idAtProvider, new_venue.siret)
            for stock in offer.stocks:
                stock.idAtProviders = offer.idAtProviders
            db.session.add(offer, offer.stocks)
            db.session.flush()
            offer_moved_count += 1
    print("Updated %s bookings to the new venue" % updated_stock_count)
    print("Moved %s offers to the new venue" % offer_moved_count)


def migrate_bookings_from_old_venue_to_new_venue(old_venue_id: int, new_venue_id: int) -> None:
    # Move manual offers from old venue to the new one
    new_venue = Venue.query.get(new_venue_id)
    manual_offer_count = Offer.query.filter(Offer.venueId == old_venue_id, Offer.idAtProvider.is_(None)).update(
        {Offer.venueId: new_venue_id}, synchronize_session=False
    )
    print("Moved %s manual offers" % manual_offer_count)
    # Update all the bookings from the old venue/offerer to the new ones
    updated_bookings_count = Booking.query.filter(Booking.venueId == old_venue_id).update(
        {Booking.venueId: new_venue_id, Booking.offererId: new_venue.managingOffererId}, synchronize_session=False
    )
    print("Updated %s bookings to new venue/offerer" % updated_bookings_count)
    # Move the synchronized bookings to the new venue (or switch their offers to the new offerer)
    migrate_bookings(old_venue_id=12123, new_venue_id=27723)
    # Deactivate the old venue offers
    deactivated_offers_ids = [
        offer_id
        for offer_id, in db.session.query(Offer.id).filter(
            Offer.venueId == old_venue_id, Offer.idAtProvider.isnot(None)
        )
    ]
    deactivated_offers_count = Offer.query.filter(Offer.venueId == old_venue_id, Offer.idAtProvider.isnot(None)).update(
        {Offer.isActive: False}, synchronize_session=False
    )
    print("Deactivated %s offers" % deactivated_offers_count)
    db.session.commit()
    # Recompute dnBookedQuantity
    over_booked: list[int] = []
    stock_ids_to_recompute = check_stock_consistency()
    for stock_id in stock_ids_to_recompute:
        try:
            recompute_dnBookedQuantity([stock_id])
            db.session.commit()
        except:  # pylint: disable=bare-except
            over_booked.append(stock_id)
            db.session.rollback()
            non_cancelled_bookings_qt = Booking.query.filter(
                Booking.stockId == stock_id, Booking.status != BookingStatus.CANCELLED
            ).count()
            Stock.query.filter(Stock.id == stock_id).update(
                {"quantity": non_cancelled_bookings_qt}, synchronize_session=False
            )
            recompute_dnBookedQuantity([stock_id])
            db.session.commit()
    print("dnBookedQuantity updated")
    print("overbooking stocks: %s" % over_booked)

    # full sync to reset the offers quantity
    fully_sync_venue(new_venue)
    print("Full sync performed")

    # synchro algolia
    search.unindex_offer_ids(deactivated_offers_ids)
    new_venue_offer_ids = [offer_id for offer_id, in db.session.query(Offer.id).filter(Offer.venueId == new_venue_id)]
    search.reindex_offer_ids(new_venue_offer_ids)
    print("Algolia syncho launched")


if __name__ == "__main__":
    migrate_bookings_from_old_venue_to_new_venue(12123, 27723)
