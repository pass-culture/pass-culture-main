"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41697-acces-aux-details-dune-offre-impossible-chargement-infini \
  -f NAMESPACE=clean_too_many_stock \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(offer_ids: list[int]) -> None:
    for offer_id in offer_ids:
        stock_count = db.session.query(offers_models.Stock).filter(offers_models.Stock.offerId == offer_id).count()
        stock_ids_to_be_removed = [
            id
            for (id,) in db.session.query(offers_models.Stock.id)
            .outerjoin(offers_models.Stock.bookings)
            .filter(
                offers_models.Stock.offerId == offer_id,
                offers_models.Stock.isExpired,
                bookings_models.Booking.id == None,
            )
            .tuples()
        ]
        logger.info(
            "Offer %d has %d stocks and %d of them have no booking and are to be deleted",
            offer_id,
            stock_count,
            len(stock_ids_to_be_removed),
        )
        db.session.query(offers_models.Stock).filter(offers_models.Stock.id.in_(stock_ids_to_be_removed)).delete()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--offer-ids", nargs="+", type=int, required=True)
    args = parser.parse_args()

    with atomic():
        main(offer_ids=args.offer_ids)
        if args.apply:
            logger.info("Finished")
        else:
            mark_transaction_as_invalid()
            logger.info("Finished dry run, rollback")
