"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=move_offers_location \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import itertools
import logging

import sqlalchemy.exc as sa_exc
from sqlalchemy import select
from sqlalchemy import update

from pcapi.app import app
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


OFFER_BATCH_SIZE = 1000


def move_offers(
    venue_id: int,
    source_locations_ids: list[int],
    target_location_id: int,
    offer_model: type[Offer] | type[CollectiveOffer] | type[CollectiveOfferTemplate],
) -> None:
    offer_ids = db.session.scalars(
        select(offer_model.id).filter(
            offer_model.venueId == venue_id,
            offer_model.offererAddressId.in_(source_locations_ids),
        )
    ).all()

    logger.info(
        "Found %i %s(s) for locations(s) %s",
        len(offer_ids),
        offer_model.__name__,
        source_locations_ids,
    )

    for batched_offer_ids in itertools.batched(offer_ids, OFFER_BATCH_SIZE):
        try:
            with atomic():
                db.session.execute(
                    update(offer_model)
                    .where(offer_model.id.in_((batched_offer_ids)))
                    .values(offererAddressId=target_location_id)
                )
        except sa_exc.OperationalError as exc:
            logger.info("Exception %s - Trying to update offer one by one", str(exc))
            with atomic():
                for offer_id in batched_offer_ids:
                    db.session.execute(
                        update(offer_model)
                        .where(offer_model.id == offer_id)
                        .values(offererAddressId=target_location_id)
                    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--venue-id", type=int, required=True)
    parser.add_argument("--target-location-id", type=int, required=True)
    parser.add_argument("--source-location-ids", type=int, action="append", required=True)
    args = parser.parse_args()

    not_dry = args.not_dry
    venue: int = args.venue_id
    source_locations: list[int] = args.source_location_ids
    target_location: int = args.target_location_id
    with atomic():
        move_offers(venue, source_locations, target_location, Offer)
        move_offers(venue, source_locations, target_location, CollectiveOffer)
        move_offers(venue, source_locations, target_location, CollectiveOfferTemplate)
        if not not_dry:
            mark_transaction_as_invalid()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
