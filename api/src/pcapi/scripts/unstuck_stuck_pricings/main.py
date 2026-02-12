"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-unstuck-stuck-pricings \
  -f NAMESPACE=unstuck_stuck_pricings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    pricings = (
        db.session.query(finance_models.Pricing)
        .join(
            offerers_models.Venue,
            (finance_models.Pricing.venueId == offerers_models.Venue.id),
        )
        .execution_options(include_deleted=True)
        .filter(
            offerers_models.Venue.isSoftDeleted.is_(True),
            finance_models.Pricing.venueId != finance_models.Pricing.pricingPointId,
            finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
            finance_models.Pricing.amount < 0,
        )
        .all()
    )
    logger.info("%s pricings to move", len(pricings))
    for pricing in pricings:
        logger.info("Moving pricing %s from venue %s to venue %s", pricing.id, pricing.venueId, pricing.pricingPointId)
        pricing.venueId = pricing.pricingPointId
        db.session.add(pricing)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
