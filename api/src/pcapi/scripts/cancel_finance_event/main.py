"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40602-cancel-uncancelled-finance-event \
  -f NAMESPACE=cancel_finance_event \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def cancel_finance_event(event: finance_models.FinanceEvent) -> None:
    """Cancel latest used-related finance event, if there is one."""

    pricing = finance_api._cancel_event_pricing(event, finance_models.PricingLogReason.MARK_AS_UNUSED)
    event.status = finance_models.FinanceEventStatus.CANCELLED
    db.session.flush()
    logger.info(
        "Cancelled finance event and its pricing",
        extra={
            "booking": event.bookingId,
            "event": event.id,
            "pricing": pricing.id if pricing else None,
        },
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    finance_event = db.session.query(finance_models.FinanceEvent).filter_by(id=50181948).one()
    cancel_finance_event(finance_event)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
