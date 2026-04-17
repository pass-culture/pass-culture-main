"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-41385-script-delete-98-offers \
  -f NAMESPACE=delete_98_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.criteria import models as criteria_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.api import delete_mediations
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_offers(offerer_id: int, eans: list[str]) -> None:
    offer_ids = db.session.scalar(
        sa.select(sa.func.array_agg(offers_models.Offer.id))
        .join(offers_models.Offer.venue)
        .filter(offers_models.Offer.ean.in_(eans))
        .filter(offerers_models.Venue.managingOffererId == offerer_id)
        .filter(offers_models.Offer.validation == offers_models.OfferValidationStatus.REJECTED)
    )

    assert offer_ids is not None  # helps mypy
    logging.info("Found %d offers to delete with EAN in %s, Offerer ID %d", len(offer_ids), eans, offerer_id)

    count = (
        db.session.query(offers_models.Stock)
        .filter(offers_models.Stock.offerId.in_(offer_ids))
        .delete(synchronize_session=False)
    )
    logging.info("Deleted %d stocks", count)

    count = (
        db.session.query(users_models.Favorite)
        .filter(users_models.Favorite.offerId.in_(offer_ids))
        .delete(synchronize_session=False)
    )
    logging.info("Deleted %d favorites", count)

    count = (
        db.session.query(criteria_models.OfferCriterion)
        .filter(criteria_models.OfferCriterion.offerId.in_(offer_ids))
        .delete(synchronize_session=False)
    )
    logging.info("Deleted %d offer-criterion associations", count)

    delete_mediations(offer_ids, reindex=False)

    count = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id.in_(offer_ids))
        .delete(synchronize_session=False)
    )
    logging.info("Deleted %d offers", count)

    # Rejected offers are not indexed. No need to unindex.


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--offerer-id", type=int, required=True)
    parser.add_argument("--eans", type=str, required=True)
    args = parser.parse_args()

    delete_offers(offerer_id=args.offerer_id, eans=args.eans.split(","))

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
