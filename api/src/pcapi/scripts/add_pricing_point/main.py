"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41200-add-pricing-point-to-finance-events \
  -f NAMESPACE=add_pricing_point \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(venue_id: int) -> None:
    finance_events = (
        db.session.query(finance_models.FinanceEvent)
        .filter(
            finance_models.FinanceEvent.venueId == venue_id,
            finance_models.FinanceEvent.status == finance_models.FinanceEventStatus.READY,
            finance_models.FinanceEvent.creationDate < datetime.datetime(year=2026, month=4, day=1),
        )
        .all()
    )
    logger.info("Found %s finance events", len(finance_events))
    for finance_event in finance_events:
        assert finance_event.booking  # helps mypy
        new_date = datetime.datetime(year=2026, month=4, day=1)  # because there are invoiced pricings before April 1st
        logger.info(
            "Updating FE %s with date %s",
            finance_event.id,
            new_date,
        )
        finance_event.pricingOrderingDate = new_date
        db.session.add(finance_event)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--venue-id", type=int, required=True)
    args = parser.parse_args()

    main(args.venue_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
