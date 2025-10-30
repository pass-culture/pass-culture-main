"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=PC-38600-redo-stuck-finance-events-of-two-venues   -f NAMESPACE=restart_finance_events   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import get_pricing_ordering_date
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(venue_id: int) -> None:
    finance_events = (
        db.session.query(finance_models.FinanceEvent)
        .filter(
            finance_models.FinanceEvent.venueId == venue_id,
            finance_models.FinanceEvent.status == finance_models.FinanceEventStatus.PENDING,
        )
        .all()
    )
    logger.info(f"Found {len(finance_events)} to work on")
    for event in finance_events:
        assert event.venue
        ppId = event.venue.current_pricing_point_id
        booking = event.booking
        assert booking

        db.session.query(finance_models.FinanceEvent).filter(
            finance_models.FinanceEvent.venueId == venue_id,
            finance_models.FinanceEvent.status == finance_models.FinanceEventStatus.PENDING,
        ).update(
            {
                "status": finance_models.FinanceEventStatus.READY,
                "pricingPointId": ppId,
                "pricingOrderingDate": get_pricing_ordering_date(booking),
            },
            synchronize_session=False,
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--venue-id", type=int, required=True)
    args = parser.parse_args()

    main(venue_id=args.venue_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
