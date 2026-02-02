"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=tcoudray-pass/PC-40046-cancel-event-tickets \
  -f NAMESPACE=cancel_event_ticket_for_cancelled_bookings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import os

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.external_bookings.api import cancel_event_ticket
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def _cancel_tickets(offer: Offer, not_dry: bool = False) -> None:
    logger.info("Cancelling tickets...", extra={"offerName": offer.name, "offerId": offer.id})

    for stock in offer.stocks:
        if stock.bookingLimitDatetime < date_utils.get_naive_utc_now():
            logger.info("Stock has expired", extra={"offerId": offer.id, "stockId": stock.id})
            continue

        for booking in stock.bookings:
            if booking.status == bookings_models.BookingStatus.CANCELLED and booking.externalBookings:
                if not_dry == False:
                    logger.info(
                        "Would have cancelled tickets",
                        extra={"bookingId": booking.id, "offerId": offer.id, "stockId": stock.id},
                    )
                    continue

                try:
                    assert offer.lastProvider  # to make mypy happy
                    cancel_event_ticket(
                        offer.lastProvider,
                        stock,
                        [external_booking.barcode for external_booking in booking.externalBookings],
                        is_booking_saved=True,
                        venue_provider=None,
                    )

                    for external_booking in booking.externalBookings:
                        db.session.delete(external_booking)
                    db.session.flush()

                    logger.info(
                        "Ticket cancelled", extra={"bookingId": booking.id, "offerId": offer.id, "stockId": stock.id}
                    )
                except Exception as exc:
                    logger.error(
                        "Unexpected error while cancelling ticket %s",
                        exc,
                        extra={"bookingId": booking.id, "offerId": offer.id, "stockId": stock.id},
                    )


def main(not_dry: bool) -> None:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f"{namespace_dir}/offers_ids.txt", encoding="utf-8") as f:
        offer_ids = f.readlines()
        for offer_id in offer_ids:
            offer = db.session.query(Offer).filter(Offer.id == int(offer_id)).one()
            _cancel_tickets(offer, not_dry)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
