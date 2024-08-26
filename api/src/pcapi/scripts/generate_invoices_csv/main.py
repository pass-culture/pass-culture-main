import argparse
import logging

from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.logging import log_elapsed
from pcapi.flask_app import app


logger = logging.getLogger(__name__)


def generate_invoices_csv(batch_id: int) -> None:
    batch = finance_models.CashflowBatch.query.get(batch_id)

    with log_elapsed(logger, "Generated CSV invoices file"):
        path = finance_api.generate_invoice_file(batch)
    drive_folder_name = finance_api._get_drive_folder_name(batch)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        finance_api._upload_files_to_google_drive(drive_folder_name, [path])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--batch-id", type=int, required=True)

    args = parser.parse_args()

    with app.app_context():
        generate_invoices_csv(args.batch_id)
