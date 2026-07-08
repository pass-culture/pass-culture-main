"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42784-mass-cancel-festival-bookings \
  -f NAMESPACE=mass_cancel_bookings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(offer_id: int, apply: bool) -> None:
    bookings = (
        db.session.query(bookings_models.Booking)
        .join(bookings_models.Booking.stock)
        .options(sa_orm.contains_eager(bookings_models.Booking.stock))
        .filter(
            offers_models.Stock.offerId == offer_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.USED,
        )
        .all()
    )
    logger.info("%s bookings to cancel", len(bookings))

    for booking in bookings:
        with atomic():
            try:
                bookings_api.mark_as_cancelled(
                    booking=booking,
                    reason=bookings_models.BookingCancellationReasons.BACKOFFICE_EVENT_CANCELLED,
                    author_id=None,
                )
            except (
                bookings_exceptions.BookingIsAlreadyUsed,
                bookings_exceptions.BookingIsAlreadyRefunded,
                bookings_exceptions.BookingIsAlreadyCancelled,
            ):
                mark_transaction_as_invalid()

            if not apply:
                mark_transaction_as_invalid()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--offer-id", type=int, required=True)
    args = parser.parse_args()

    main(args.offer_id, args.apply)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
