import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    finance_event_statuses = {finance_models.FinanceEventStatus.READY, finance_models.FinanceEventStatus.PENDING}
    limit_date = datetime.datetime.utcnow() - datetime.timedelta(days=2)

    logger.info("Starting to fix USED bookings")
    bookings: list[educational_models.CollectiveBooking] = (
        educational_models.CollectiveBooking.query.join(
            finance_models.FinanceEvent,
            finance_models.FinanceEvent.collectiveBookingId == educational_models.CollectiveBooking.id,
        )
        .join(
            educational_models.CollectiveStock,
            educational_models.CollectiveBooking.collectiveStockId == educational_models.CollectiveStock.id,
        )
        .filter(
            educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.USED,
            finance_models.FinanceEvent.status.in_(finance_event_statuses),
            educational_models.CollectiveStock.endDatetime >= limit_date,
        )
        .all()
    )

    logger.info("Found %s USED bookings to fix", len(bookings))
    try:
        event_ids_to_delete = set()
        for booking in bookings:
            events = [event for event in booking.finance_events if event.status in finance_event_statuses]
            if len(events) != 1:
                logger.error("Could not find one ready or pending event for booking with id %s", booking.id)
                db.session.rollback()
                raise ValueError

            booking.status = educational_models.CollectiveBookingStatus.CONFIRMED
            booking.dateUsed = None
            event_ids_to_delete.add(events[0].id)
            logger.info("Processed booking with id %s", booking.id)
            logger.info("Marked finance event with id %s to delete", events[0].id)

        logger.info("Deleting finance events")
        finance_models.FinanceEvent.query.filter(finance_models.FinanceEvent.id.in_(event_ids_to_delete)).delete()
    except:
        logger.error("Error while fixing USED bookings")
        db.session.rollback()
        raise

    if args.not_dry:
        logger.info("Committing fixed bookings")
        db.session.commit()
    else:
        logger.info("Finished dry run for fixing USED bookings, rollbacking")
        db.session.rollback()
