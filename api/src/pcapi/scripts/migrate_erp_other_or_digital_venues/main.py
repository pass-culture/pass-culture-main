"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39450-rattrapage-des-erp-venues-autre-ou-offre-numerique-avec-offres \
  -f NAMESPACE=migrate_erp_other_or_digital_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import func

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.schemas as offerers_schemas
import pcapi.core.offers.models as offers_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    query = (
        db.session.query(
            offerers_models.Venue.id,
            offers_models.Offer.subcategoryId,
            func.count(offers_models.Offer.id).label("total"),
        )
        .join(offerers_models.Venue.offers)
        .filter(
            offerers_models.Venue.isOpenToPublic == True,
            offerers_models.Venue.activity.is_(None),
            offerers_models.Venue.venueTypeCode.in_(
                [offerers_schemas.VenueTypeCode.OTHER, offerers_schemas.VenueTypeCode.DIGITAL]
            ),
        )
        .group_by(offerers_models.Venue.id, offers_models.Offer.subcategoryId)
        .order_by(offerers_models.Venue.id, "total")
    )
    print(query)


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
