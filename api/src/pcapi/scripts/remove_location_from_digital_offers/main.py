"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39691-impossibilite-de-modifier-une-offre-numerique-rattrapage-des-offres \
  -f NAMESPACE=remove_location_from_digital_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.categories import subcategories
from pcapi.core.offers import models as offers_models
from pcapi.models import db


ONLINE_SUBCATEGORIES = [subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.is_online_only]


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    logger.info("Script starting")
    offer_ids = [
        result
        for (result,) in db.session.query(offers_models.Offer.id)
        .filter(
            offers_models.Offer.offererAddressId != None, offers_models.Offer.subcategoryId.in_(ONLINE_SUBCATEGORIES)
        )
        .all()
    ]
    logger.info("%s offer ids identified", len(offer_ids))
    updated_rows_qt = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id.in_(offer_ids))
        .update({offers_models.Offer.offererAddressId: None}, synchronize_session=False)
    )
    logger.info("updated %s offers", updated_rows_qt)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
