import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        logger.info("Starting to correct bookings scheduled to be reimbursed")
        bookings = (
            educational_models.CollectiveBooking.query.join(
                finance_models.Pricing,
                finance_models.Pricing.collectiveBookingId == educational_models.CollectiveBooking.id,
            )
            .join(
                finance_models.FinanceEvent,
                finance_models.FinanceEvent.collectiveBookingId == educational_models.CollectiveBooking.id,
            )
            .join(
                educational_models.CollectiveStock,
                educational_models.CollectiveBooking.collectiveStockId == educational_models.CollectiveStock.id,
            )
            .filter(
                finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
                finance_models.FinanceEvent.status == finance_models.FinanceEventStatus.PRICED,
                educational_models.CollectiveStock.endDatetime != educational_models.CollectiveStock.beginningDatetime,
                educational_models.CollectiveStock.endDatetime >= datetime.datetime(2024, 10, 1),
            )
        )

        booking_ids = [booking.id for booking in bookings]
        logger.info("Executing the script for %s bookings", len(booking_ids))
        logger.info("Cancelling the pricing for the following ids: %s", booking_ids)

        for booking in bookings:
            logger.info("Cancelling the event and pricing for the booking_id: %s", booking.id)
            finance_api.cancel_latest_event(booking)
            logger.info("Adding a new correct event for the booking_id: %s", booking.id)
            event = finance_api.add_event(finance_models.FinanceEventMotive.BOOKING_USED, booking=booking)
            logger.info("Event created: %s", event.id)
            event.valueDate = event.pricingOrderingDate
            db.session.add(event)

    except Exception:
        logger.error("Rollbacking due to Exception")
        db.session.rollback()
        raise

    if args.dry_run:
        logger.info("Rollbacking due to dry-run")
        db.session.rollback()
    else:
        logger.info("Commit new events to db")
        db.session.commit()
