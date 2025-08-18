"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/master/api/src/pcapi/scripts/generate_changing_ba_csv/main.py

"""

import logging

from pcapi.app import app
from pcapi.core.finance import api
from pcapi.core.finance import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def generate_changing_BA_csv(batch: models.CashflowBatch) -> None:
    logger.info("Generating payment files")

    file_paths = {}

    previous_batch = (
        db.session.query(models.CashflowBatch)
        .filter(models.CashflowBatch.cutoff < batch.cutoff)
        .order_by(models.CashflowBatch.cutoff.desc())
        .limit(1)
        .one_or_none()
    )
    if previous_batch:
        logger.info("Generating changing bank accounts file")
        file_paths["changing_bank_accounts"] = api._generate_changing_bank_accounts_file(
            previous_batch.cutoff, batch.cutoff
        )

    drive_folder_name = api._get_drive_folder_name(batch)
    api._upload_files_to_google_drive(drive_folder_name, file_paths.values())


if __name__ == "__main__":
    app.app_context().push()

    batch = db.session.query(models.CashflowBatch).order_by(models.CashflowBatch.cutoff.desc()).limit(1).one_or_none()
    generate_changing_BA_csv(batch)
