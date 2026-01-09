"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39634-amelioration-des-localisations-repasser-les-offres-de-l-api-publique-sur-des-oa-sans-type \
  -f NAMESPACE=fix_offer_to_location_without_type \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

import pcapi.core.offerers.models as offerers_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    nb_OA = (
        db.session.query(sa.func.count(offerers_models.OffererAddress.id))
        .filter(offerers_models.OffererAddress.type == offerers_models.LocationType.VENUE_LOCATION)
        .order_by(offerers_models.OffererAddress.id.desc)
        .scalar()
    )
    # using limit at 1000 and offset keeps the query planer with faster requests than using
    # cursors or whatever
    i = 0
    while i < nb_OA:
        db.session.query()


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
