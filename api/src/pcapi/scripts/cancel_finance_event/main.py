"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=cancel_finance_event \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import _cancel_event_pricing
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(event_id: int) -> None:
    event = (
        db.session.query(finance_models.FinanceEvent).filter(finance_models.FinanceEvent.id == event_id).one_or_none()
    )
    if event:
        pricing = _cancel_event_pricing(event, finance_models.PricingLogReason.MARK_AS_UNUSED)
        event.status = finance_models.FinanceEventStatus.CANCELLED
        db.session.add(event)
        db.session.flush()
        assert event.booking
        logger.info(
            "Cancelled finance event and its pricing",
            extra={
                "booking": event.booking.id,
                "event": event.id,
                "pricing": pricing.id if pricing else None,
            },
        )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--event-id", required=True, type=int)
    args = parser.parse_args()

    main(args.event_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
