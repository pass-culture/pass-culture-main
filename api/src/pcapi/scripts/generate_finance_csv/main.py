import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import _get_drive_folder_name
from pcapi.core.finance.api import _upload_files_to_google_drive
from pcapi.core.finance.api import generate_invoice_file
from pcapi.core.logging import log_elapsed


logger = logging.getLogger(__name__)

app.app_context().push()


def main() -> None:
    batch = finance_models.CashflowBatch.query.get(2066)
    with log_elapsed(logger, "Generated CSV invoices file"):
        path = generate_invoice_file(batch)
    drive_folder_name = _get_drive_folder_name(batch)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        _upload_files_to_google_drive(drive_folder_name, [path])


main()
