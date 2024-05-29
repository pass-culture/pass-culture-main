import argparse
import logging

# pylint: disable=unused-import
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import _delete_dependent_pricings
from pcapi.core.offers import models as offers_models
from pcapi.models import db


OLD_VENUE_ID = 66681
OLD_OFFERER_ID = 27600
NEW_VENUE_ID = NEW_PRICING_POINT_ID = 68449
NEW_OFFERER_ID = 7050

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="PC-29940 : Move offers from venue 66681 to venue 68449")
    parser.add_argument(
        "--not-dry",
        action="store_true",
        help="set to really process (dry-run by default)",
    )
    args = parser.parse_args()

    logger.info("PC-29940 : Start update")

    # OFFER
    offers_models.Offer.query.filter(offers_models.Offer.venueId == OLD_VENUE_ID).update({"venueId": NEW_VENUE_ID})
    db.session.flush()

    # PRICE_CATEGORY
    old_price_category_label = offers_models.PriceCategoryLabel.query.filter(
        offers_models.PriceCategoryLabel.venueId == OLD_VENUE_ID
    ).one()  # there is only one
    new_price_category_label = offers_models.PriceCategoryLabel.query.filter(
        offers_models.PriceCategoryLabel.venueId == NEW_VENUE_ID,
        offers_models.PriceCategoryLabel.label == old_price_category_label.label,
    ).one()  # there is only one with that label
    offers_models.PriceCategory.query.filter(
        offers_models.PriceCategory.priceCategoryLabel == old_price_category_label
    ).update({"priceCategoryLabelId": new_price_category_label.id})
    db.session.flush()

    ## BOOKING
    bookings_models.Booking.query.filter(bookings_models.Booking.venueId == OLD_VENUE_ID).update(
        {"venueId": NEW_VENUE_ID, "offererId": NEW_OFFERER_ID}
    )
    db.session.flush()

    ## PRICING
    pricings = finance_models.Pricing.query.filter(finance_models.Pricing.venueId == OLD_VENUE_ID).all()
    pricing_ids = [pricing.id for pricing in pricings]
    print(f"{len(pricing_ids)} pricings to delete")
    finance_models.PricingLine.query.filter(
        finance_models.PricingLine.pricingId.in_(pricing_ids),
    ).delete(synchronize_session=False)
    finance_models.Pricing.query.filter(finance_models.Pricing.venueId == OLD_VENUE_ID).delete(
        synchronize_session=False
    )  # No invoiced pricings because old offerer never had a bank account
    db.session.flush()

    ## FINANCE_EVENT
    finance_events = finance_models.FinanceEvent.query.filter(
        finance_models.FinanceEvent.venueId == OLD_VENUE_ID
    ).all()  # all PRICED
    for event in finance_events:
        event.status = finance_models.FinanceEventStatus.READY
        event.venueId = NEW_PRICING_POINT_ID
        event.pricingPointId = NEW_PRICING_POINT_ID
        db.session.add(event)
    db.session.flush()

    earliest_event = min(finance_events, key=lambda event: event.id)
    _delete_dependent_pricings(earliest_event, "PC-29940 : Move offers from venue 66681 to venue 68449")

    if args.not_dry:
        db.session.commit()
        logger.info("PC-29940 : Committed")
    else:
        db.session.rollback()
        logger.info("PC-29940 : Rollbacked")

    logger.info("PC-29940 : Done")
