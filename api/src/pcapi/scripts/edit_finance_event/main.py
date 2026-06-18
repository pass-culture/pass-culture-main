"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42455-edit-finance-event \
  -f NAMESPACE=edit_finance_event \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.finance.models as finance_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)

FINANCE_EVENT_ID = 50732922


def main() -> None:
    finance_event_to_edit = (
        db.session.query(finance_models.FinanceEvent).filter(finance_models.FinanceEvent.id == FINANCE_EVENT_ID).one()
    )
    finance_event_to_edit.pricingOrderingDate = date_utils.get_naive_utc_now()
    db.session.add(finance_event_to_edit)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
