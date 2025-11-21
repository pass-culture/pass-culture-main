"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-script-set-finance-incident-to-invoiced \
  -f NAMESPACE=set_incident_invoiced \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    finance_incidents = (
        db.session.query(finance_models.FinanceIncident)
        .join(finance_models.BookingFinanceIncident)
        .join(finance_models.FinanceEvent)
        .join(finance_models.Pricing)
        .filter(finance_models.Pricing.status == finance_models.PricingStatus.INVOICED)
        .filter(finance_models.FinanceIncident.status == finance_models.IncidentStatus.VALIDATED)
        .all()
    )
    for finance_incident in finance_incidents:
        finance_incident.status = finance_models.IncidentStatus.INVOICED
        db.session.add(finance_incident)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
