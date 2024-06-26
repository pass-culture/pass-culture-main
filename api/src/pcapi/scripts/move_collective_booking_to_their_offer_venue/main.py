import argparse
import logging

import pcapi.core.educational.models as educational_models
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers.models import VenuePricingPointLink
from pcapi.models import db


logger = logging.getLogger(__name__)


# I redefine get_pricing_point_link to avoid the autoflush from getting the pricing_point_links from the booking's pricing point
def get_pricing_point_link(
    coll_booking: educational_models.CollectiveBooking,
) -> VenuePricingPointLink:
    """Return the venue-pricing point link to use at the time the
    booking was marked as used.
    """
    timestamp = coll_booking.dateUsed
    links = coll_booking.collectiveStock.collectiveOffer.venue.pricing_point_links

    # Look for a link that was active at the requested date.
    for link in links:
        if timestamp < link.timespan.lower:
            continue
        if not link.timespan.upper or timestamp < link.timespan.upper:
            return link

    # If a link was added after and it's still active, we can use it.
    # On the other hand, if there are two links, and the second one is
    # inactive, and the booking has been used before the *first* link,
    # it's not clear what we should do (and we'll raise below).
    links_after = [link for link in links if timestamp < link.timespan.lower]
    if len(links_after) == 1 and links_after[0].timespan.upper is None:
        return links_after[0]

    # Otherwise, it's not clear what we should do. Raise an error so
    # that we can investigate.
    raise ValueError(f"Could not find pricing point for booking {coll_booking.id}")


def get_lost_bookings() -> list[educational_models.CollectiveBooking]:
    lost_bookings = (
        educational_models.CollectiveBooking.query.join(educational_models.CollectiveStock)
        .join(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveBooking.venueId != educational_models.CollectiveOffer.venueId)
    ).all()
    return lost_bookings


def update_cancelled_booking(
    collective_booking: educational_models.CollectiveBooking,
) -> None:
    collective_booking.venueId = collective_booking.collectiveStock.collectiveOffer.venueId
    db.session.add(collective_booking)


def update_used_booking(
    collective_booking: educational_models.CollectiveBooking,
) -> None:
    collective_booking.venueId = collective_booking.collectiveStock.collectiveOffer.venueId

    finance_event = collective_booking.finance_events[0]  # only one each time, I checked
    logger.info("PC-29354 : Update pending finance event")
    if finance_event.status == finance_models.FinanceEventStatus.PENDING:
        finance_event.venueId = collective_booking.collectiveStock.collectiveOffer.venueId
        if collective_booking.collectiveStock.collectiveOffer.venue.current_pricing_point_id:
            # Copied from finance_api.get_pricing_ordering_date()
            # I used collectiveStock.beginningDatetime, because it was about old data, but
            # if you reuse that script, you should probably use collectiveStock.endDatetime (as in get_pricing_ordering_date)
            new_pricing_ordering_date = max(
                get_pricing_point_link(collective_booking).timespan.lower,
                collective_booking.collectiveStock.beginningDatetime or collective_booking.dateUsed,
                collective_booking.dateUsed,
            )
            finance_event.pricingPointId = (
                collective_booking.collectiveStock.collectiveOffer.venue.current_pricing_point_id
            )
            finance_event.pricingOrderingDate = new_pricing_ordering_date
            finance_event.status = finance_models.FinanceEventStatus.READY

    elif finance_event.status == finance_models.FinanceEventStatus.PRICED:
        logger.info("PC-29354 : Update priced finance event")
        pricing = finance_models.Pricing.query.filter(
            finance_models.Pricing.collectiveBookingId == collective_booking.id
        ).one()
        finance_models.PricingLine.query.filter(finance_models.PricingLine.pricingId == pricing.id).delete()
        finance_models.PricingLog.query.filter(finance_models.PricingLog.pricingId == pricing.id).delete()
        finance_models.Pricing.query.filter(
            finance_models.Pricing.collectiveBookingId == collective_booking.id
        ).delete()
        db.session.flush()

        finance_event.venueId = collective_booking.collectiveStock.collectiveOffer.venueId
        if collective_booking.collectiveStock.collectiveOffer.venue.current_pricing_point_id:
            # Copied from finance_api.get_pricing_ordering_date()
            # I used collectiveStock.beginningDatetime, because it was about old data, but
            # if you reuse that script, you should probably use collectiveStock.endDatetime (as in get_pricing_ordering_date)
            new_pricing_ordering_date = max(
                get_pricing_point_link(collective_booking).timespan.lower,
                collective_booking.collectiveStock.beginningDatetime or collective_booking.dateUsed,
                collective_booking.dateUsed,
            )
            finance_event.pricingPointId = (
                collective_booking.collectiveStock.collectiveOffer.venue.current_pricing_point_id
            )
            finance_event.pricingOrderingDate = new_pricing_ordering_date
            finance_event.status = finance_models.FinanceEventStatus.READY
        else:
            finance_event.pricingPointId = None
            finance_event.pricingOrderingDate = None
            finance_event.status = finance_models.FinanceEventStatus.PENDING

    db.session.add(collective_booking)
    db.session.add(finance_event)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    logger.info("Starting")
    parser = argparse.ArgumentParser(description="PC-29354 : Move collective bookings on their offer's venue")
    parser.add_argument(
        "--not-dry",
        action="store_true",
        help="set to really process (dry-run by default)",
    )
    args = parser.parse_args()

    bookings = get_lost_bookings()
    for booking in bookings:
        if booking.status == educational_models.CollectiveBookingStatus.CANCELLED:
            logger.info("PC-29354 : Update cancelled bookings")
            update_cancelled_booking(booking)
        db.session.flush()

    for booking in bookings:
        if booking.status == educational_models.CollectiveBookingStatus.USED:
            logger.info("PC-29354 : Update used bookings")
            update_used_booking(booking)
        db.session.flush()

    # there are also reimbursed booking, but it's a bit late and quite annoying to move them

    if args.not_dry:
        db.session.commit()
        logger.info("PC-29354 : Committed")
    else:
        db.session.rollback()
        logger.info("PC-29354 : Rollbacked")
    logger.info("It's over")
