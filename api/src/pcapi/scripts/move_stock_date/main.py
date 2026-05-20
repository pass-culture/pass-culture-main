"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41922-move-stock-forward-in-time \
  -f NAMESPACE=move_stock_date \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def main(stock_id: int) -> None:
    stock = db.session.query(offers_models.Stock).filter(offers_models.Stock.id == stock_id).one_or_none()

    if not stock:
        logger.info("Where's the stock gone ?")
        return

    for booking in stock.bookings:
        if booking.status == bookings_models.BookingStatus.USED:
            bookings_api.mark_as_unused(booking)
    new_datetime = datetime(year=2026, month=11, day=8, hour=19, minute=30, second=0, tzinfo=ZoneInfo("Europe/Paris"))
    stock.beginningDatetime = date_utils.to_naive_utc_datetime(new_datetime)
    stock.bookingLimitDatetime = date_utils.to_naive_utc_datetime(new_datetime)
    db.session.add(stock)
    db.session.flush()


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
