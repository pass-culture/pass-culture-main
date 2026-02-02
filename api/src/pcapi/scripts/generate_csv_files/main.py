"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-regenerate-finance-csv \
  -f NAMESPACE=generate_csv_files \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

from pcapi.app import app
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    file_paths = {}

    batch = db.session.query(finance_models.CashflowBatch).filter(finance_models.CashflowBatch.id == 2105).one()
    previous_batch = (
        db.session.query(finance_models.CashflowBatch).filter(finance_models.CashflowBatch.id == 2104).one()
    )

    if previous_batch:
        logger.info("Generating changing bank accounts file")
        file_paths["changing_bank_accounts"] = finance_api._generate_changing_bank_accounts_file(
            previous_batch.cutoff, batch.cutoff
        )

    logger.info("Generating payments file")
    file_paths["payments"] = finance_api._generate_payments_file(batch)

    logger.info(
        "Finance files have been generated",
        extra={"paths": [str(path) for path in file_paths.values()]},
    )
    drive_folder_name = finance_api._get_drive_folder_name(batch)
    finance_api._upload_files_to_google_drive(drive_folder_name, file_paths.values())
