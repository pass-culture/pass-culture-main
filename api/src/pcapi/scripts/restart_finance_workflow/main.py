"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-fix-finance-workflow \
  -f NAMESPACE=restart_finance_workflow \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    batch = db.session.query(finance_models.CashflowBatch).filter(finance_models.CashflowBatch.id == 2103).one()
    finance_api.generate_invoices_and_debit_notes(batch)
