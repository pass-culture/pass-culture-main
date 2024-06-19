import logging

from pcapi.core.finance import api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.core.logging import log_elapsed


logger = logging.getLogger(__name__)


def store_invoices(batch: finance_models.CashflowBatch) -> None:
    """Store all invoices."""
    with log_elapsed(logger, "Generated CSV invoices file"):
        path = finance_api.generate_invoice_file(batch)
    drive_folder_name = finance_api._get_drive_folder_name(batch)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        finance_api._upload_files_to_google_drive(drive_folder_name, [path])


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        latest_batch = finance_models.CashflowBatch.query.filter(finance_models.CashflowBatch.id == 2063).one()
        store_invoices(latest_batch)
