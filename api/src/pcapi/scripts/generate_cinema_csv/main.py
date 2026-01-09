"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-script-generate-cgr-kinepolis-csv \
  -f NAMESPACE=generate_cinema_csv \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

from pcapi.app import app
from pcapi.core.finance.models import CashflowBatch
from pcapi.models import db
from pcapi.scripts.pro.upload_reimbursement_csv_to_offerer_drive import export_csv_and_send_notification_emails


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    batch = db.session.query(CashflowBatch).filter(CashflowBatch.id == 2103).one()
    export_csv_and_send_notification_emails(batch.id, batch.label)
