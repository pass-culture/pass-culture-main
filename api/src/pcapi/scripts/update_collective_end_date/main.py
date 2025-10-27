"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=master   -f NAMESPACE=update_collective_end_date   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db


logger = logging.getLogger(__name__)


COLLECTIVE_BOOKING_IDS_ENDING_IN_4202 = [398354, 395087]
COLLECTIVE_BOOKING_IDS_ENDING_IN_2026 = [412860]


def get_booking(booking_id: int) -> models.CollectiveBooking:
    return (
        db.session.query(models.CollectiveBooking)
        .options(sa_orm.joinedload(models.CollectiveBooking.collectiveStock))
        .filter(models.CollectiveBooking.id == booking_id)
        .one()
    )


def set_end_datetime_tomorrow(stock: models.CollectiveStock) -> None:
    logger.info("Found stock %s with endDatetime %s", stock.id, stock.endDatetime)

    # tomorrow at the same time as original value
    time = stock.endDatetime.time()
    stock.endDatetime = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), time=time)

    logger.info("Set stock %s endDatetime to %s", stock.id, stock.endDatetime)


def main() -> None:
    for booking_id in COLLECTIVE_BOOKING_IDS_ENDING_IN_4202:
        booking = get_booking(booking_id)

        stock = booking.collectiveStock
        if stock.endDatetime.year != 4202:
            raise ValueError("End year is not as expected for stock %s", stock.id)

        set_end_datetime_tomorrow(stock)
        db.session.flush()

    for booking_id in COLLECTIVE_BOOKING_IDS_ENDING_IN_2026:
        booking = get_booking(booking_id)

        stock = booking.collectiveStock
        if stock.endDatetime.year != 2026:
            raise ValueError("End year is not as expected for stock %s", stock.id)

        set_end_datetime_tomorrow(stock)
        db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
