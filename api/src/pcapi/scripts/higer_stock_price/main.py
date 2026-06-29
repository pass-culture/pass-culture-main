"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42632-update-too-lowered-stock-price \
  -f NAMESPACE=higer_stock_price \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import decimal
import logging

from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def main(stock_id: int) -> None:
    new_price = decimal.Decimal("67.5")

    stock = db.session.query(offers_models.Stock).filter(offers_models.Stock.id == stock_id).one()
    old_price = stock.price
    stock.price = new_price
    db.session.add(stock)

    bookings = db.session.query(bookings_models.Booking).filter(bookings_models.Booking.stockId == stock_id).all()
    booking_ids = []
    for booking in bookings:
        booking_ids.append(booking.id)
        booking.amount = decimal.Decimal("67.5")
        db.session.add(booking)

    pricings = db.session.query(finance_models.Pricing).filter(finance_models.Pricing.bookingId.in_(booking_ids)).all()
    pricing_ids = [pricing.id for pricing in pricings]
    db.session.query(finance_models.PricingLine).filter(finance_models.PricingLine.pricingId.in_(pricing_ids)).delete(
        synchronize_session=False
    )
    db.session.query(finance_models.Pricing).filter(finance_models.Pricing.bookingId.in_(booking_ids)).delete()

    finance_events = (
        db.session.query(finance_models.FinanceEvent)
        .filter(
            finance_models.FinanceEvent.bookingId.in_(booking_ids),
        )
        .all()
    )
    for finance_event in finance_events:
        finance_event.status = finance_models.FinanceEventStatus.READY
        finance_event.pricingOrderingDate = date_utils.get_naive_utc_now()
        db.session.add(finance_event)

    logger.info(
        "A past stock price was updated by an administrator",
        extra={
            "user_id": "PC-42632",
            "stock_id": stock_id,
            "old_price": old_price,
            "new_price": new_price,
        },
    )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--stock-id", type=int, required=True)
    args = parser.parse_args()

    main(args.stock_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
