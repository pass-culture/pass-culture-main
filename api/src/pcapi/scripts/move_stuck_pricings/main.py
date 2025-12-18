"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-move-stuck-virtual-pricings \
  -f NAMESPACE=move_stuck_pricings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.models as finance_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    concerned_pricings = (
        db.session.query(finance_models.Pricing)
        .join(bookings_models.Booking, bookings_models.Booking.id == finance_models.Pricing.bookingId)
        .filter(
            finance_models.Pricing.amount < 0,
            finance_models.Pricing.status == finance_models.PricingStatus.VALIDATED,
            finance_models.Pricing.venueId != finance_models.Pricing.pricingPointId,
            bookings_models.Booking.venueId == finance_models.Pricing.pricingPointId,
        )
        .all()
    )
    logger.info("%s pricings will be moved", len(concerned_pricings))
    for pricing in concerned_pricings:
        logger.info("Moving pricing %s from venue %s to venue %s", pricing.id, pricing.venueId, pricing.pricingPointId)
        pricing.venueId = pricing.pricingPointId
        db.session.add(pricing)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
