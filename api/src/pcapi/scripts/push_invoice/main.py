"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-43246-script-push-invoice \
  -f NAMESPACE=push_invoice \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--invoice-ref", type=str, required=True)
    args = parser.parse_args()

    logger.info("Push invoice %s", args.invoice_ref)
    invoice = db.session.query(finance_models.Invoice).filter_by(reference=args.invoice_ref).one()
    response_data = finance_backend.push_invoice(invoice.id)
    logger.info("Invoice data: %s", response_data)

    logger.info("Get invoice %s", args.invoice_ref)
    invoice_data = finance_backend.get_invoice(args.invoice_ref)
    logger.info("Invoice data: %s", invoice_data)
