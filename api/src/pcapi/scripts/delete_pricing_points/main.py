"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-38601-delete-unused-pricing-points-to-fix-bookings \
  -f NAMESPACE=delete_pricing_points \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offerers.models import VenuePricingPointLink
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    db.session.query(VenuePricingPointLink).filter(VenuePricingPointLink.id == 7447).delete()
    db.session.query(VenuePricingPointLink).filter(VenuePricingPointLink.id == 15617).delete()
    db.session.query(VenuePricingPointLink).filter(VenuePricingPointLink.id == 16445).delete()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
