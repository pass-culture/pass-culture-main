import argparse
import logging
import typing

import sqlalchemy as sqla

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import _get_revenue_period
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def _delete_dependent_pricings(
    event: finance_models.FinanceEvent,
    log_message: str,
    pricing_points_overriding_pricing_ordering: typing.Iterable[int] = (),
) -> None:
    """Delete pricings for events that should be priced after the
    requested ``event``.

    See note in the module docstring for further details.

    pricing_points_overriding_pricing_ordering : a list of pricing point ids.
    In a script, you might have to add new pricings to a cutoff period that already
    has reimbursed pricings that can't be deleted (and so you can't compute the new
    pricing order). But sometimes, the order would not change the pricing value (because
    there is a custom reimbursement rule, or the pricing point's revenue would not change enough to
    change the reimbursement rule, etc), so you can add the pricing point to the list, and the pricings will be moved as you needed.
    """
    revenue_period_start, revenue_period_end = _get_revenue_period(event.valueDate)

    pricings = (
        finance_models.Pricing.query.filter(
            finance_models.Pricing.pricingPoint == event.pricingPoint,
        )
        .join(finance_models.Pricing.event)
        .filter(
            finance_models.Pricing.valueDate.between(revenue_period_start, revenue_period_end),
            sqla.func.ROW(finance_models.FinanceEvent.pricingOrderingDate, finance_models.FinanceEvent.id)
            > sqla.func.ROW(event.pricingOrderingDate, event.id),
        )
    )

    pricings = pricings.all()
    if not pricings:
        return
    pricing_ids = {pricing.id for pricing in pricings}
    events_already_priced = {pricing.eventId for pricing in pricings}
    for pricing in pricings:
        if pricing.status not in finance_models.DELETABLE_PRICING_STATUSES:
            assert event.pricingPointId  # helps mypy
            if event.pricingPointId in (pricing_points_overriding_pricing_ordering):
                pricing_ids.remove(pricing.id)
                events_already_priced.remove(pricing.eventId)
                logger.info(
                    "Found non-deletable pricing for a pricing point that has an older event to price or cancel (special case for problematic pricing points)",
                    extra={
                        "event_being_priced_or_cancelled": event.id,
                        "older_pricing": pricing.id,
                        "older_pricing_status": pricing.status,
                        "pricing_point": event.pricingPointId,
                    },
                )
                continue
            logger.error(
                "Found non-deletable pricing for a pricing point that has an older event to price or cancel",
                extra={
                    "event_being_priced_or_cancelled": event.id,
                    "older_pricing": pricing.id,
                    "older_pricing_status": pricing.status,
                    "pricing_point": event.pricingPointId,
                },
            )
            raise finance_exceptions.NonCancellablePricingError()

    if not pricing_ids:
        return

    # Do not reuse the `pricings` query. It should not have changed
    # since the beginning of the function (since we should have an
    # exclusive lock on the pricing point to avoid that)... but let's
    # be defensive.
    lines = finance_models.PricingLine.query.filter(finance_models.PricingLine.pricingId.in_(pricing_ids))
    lines.delete(synchronize_session=False)
    logs = finance_models.PricingLog.query.filter(finance_models.PricingLog.pricingId.in_(pricing_ids))
    logs.delete(synchronize_session=False)
    pricings = finance_models.Pricing.query.filter(finance_models.Pricing.id.in_(pricing_ids))
    pricings.delete(synchronize_session=False)

    finance_models.FinanceEvent.query.filter(
        finance_models.FinanceEvent.id.in_(events_already_priced),
        finance_models.FinanceEvent.status == finance_models.FinanceEventStatus.PRICED,
    ).update(
        {"status": finance_models.FinanceEventStatus.READY},
        synchronize_session=False,
    )
    logger.info(
        log_message,
        extra={
            "event_being_priced_or_cancelled": event.id,
            "events_already_priced": events_already_priced,
            "pricing_point": event.pricingPointId,
        },
    )


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="PC-30457 : Move offers from old venue to new venue")
    parser.add_argument(
        "--not-dry",
        action="store_true",
        help="set to really process (dry-run by default)",
    )
    parser.add_argument("--new-venue-id", type=int, required=True, help="New venue id")
    parser.add_argument("--old-venue-id", type=int, required=True, help="Old venue id")
    parser.add_argument("--new-offerer-id", type=int, required=True, help="New offerer id")
    args = parser.parse_args()

    logger.info("PC-30457 : Start update")
    new_pricing_point_id = new_venue_id = args.new_venue_id
    old_venue_id = args.old_venue_id
    new_offerer_id = args.new_offerer_id

    # OFFER
    offers_models.Offer.query.filter(offers_models.Offer.venueId == old_venue_id).update(
        {"venueId": new_venue_id, "isActive": False}
    )
    db.session.flush()

    # COLLECTIVE OFFER
    educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.venueId == old_venue_id).update(
        {"venueId": new_venue_id, "isActive": False}
    )
    db.session.flush()

    # PRICE_CATEGORY
    old_price_category_label = offers_models.PriceCategoryLabel.query.filter(
        offers_models.PriceCategoryLabel.venueId == old_venue_id
    ).one()  # there is only one
    new_price_category_label = offers_models.PriceCategoryLabel.query.filter(
        offers_models.PriceCategoryLabel.venueId == new_venue_id,
        offers_models.PriceCategoryLabel.label == old_price_category_label.label,
    ).one()  # there is only one with that label
    offers_models.PriceCategory.query.filter(
        offers_models.PriceCategory.priceCategoryLabel == old_price_category_label
    ).update({"priceCategoryLabelId": new_price_category_label.id})
    db.session.flush()

    ## BOOKING
    bookings_models.Booking.query.filter(bookings_models.Booking.venueId == old_venue_id).update(
        {"venueId": new_venue_id, "offererId": new_offerer_id}
    )
    db.session.flush()

    ## COLLECTIVE BOOKING
    educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.venueId == old_venue_id
    ).update({"venueId": new_venue_id, "offererId": new_offerer_id})
    db.session.flush()

    ## PRICING
    pricings_to_delete = finance_models.Pricing.query.filter(finance_models.Pricing.venueId == old_venue_id).all()
    pricing_to_deletet_ids = [pricing.id for pricing in pricings_to_delete]
    print(f"{len(pricing_to_deletet_ids)} pricings to delete")
    finance_models.PricingLine.query.filter(
        finance_models.PricingLine.pricingId.in_(pricing_to_deletet_ids),
    ).delete(synchronize_session=False)
    finance_models.Pricing.query.filter(finance_models.Pricing.venueId == old_venue_id).delete(
        synchronize_session=False
    )  # No invoiced pricings because old offerer never had a bank account
    db.session.flush()

    ## FINANCE_EVENT
    finance_events = finance_models.FinanceEvent.query.filter(
        finance_models.FinanceEvent.venueId == old_venue_id
    ).all()  # all PRICED
    for event_to_move in finance_events:
        event_to_move.status = finance_models.FinanceEventStatus.READY
        event_to_move.venueId = new_pricing_point_id
        event_to_move.pricingPointId = new_pricing_point_id
        db.session.add(event_to_move)
    db.session.flush()

    for event_to_move in finance_events:
        _delete_dependent_pricings(
            event_to_move,
            f"PC-30457 : Move offers from venue {old_venue_id} to venue {new_venue_id}",
            [new_pricing_point_id],
        )

    if args.not_dry:
        db.session.commit()
        logger.info("PC-30457 : Committed")
    else:
        db.session.rollback()
        logger.info("PC-30457 : Rollbacked")

    logger.info("PC-30457 : Done")
