"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42583-lower-price-for-stock-with-multiple-prices \
  -f NAMESPACE=lower_stock_price \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import decimal
import logging

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(stock_id: int) -> None:
    amount_to_remove = decimal.Decimal("35")

    stock = db.session.query(offers_models.Stock).filter(offers_models.Stock.id == stock_id).one()
    stock.price = stock.price - amount_to_remove
    db.session.add(stock)
    db.session.query(bookings_models.Booking).filter(
        bookings_models.Booking.stockId == stock_id,
        bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
    ).update({bookings_models.Booking.amount: bookings_models.Booking.amount - amount_to_remove})

    logger.info(
        "A past stock price was updated by an administrator",
        extra={
            "user_id": "PC-42583",
            "stock_id": stock_id,
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
