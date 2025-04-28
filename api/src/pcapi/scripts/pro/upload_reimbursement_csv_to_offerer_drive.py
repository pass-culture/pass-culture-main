import csv
import logging
import pathlib
import tempfile

from sqlalchemy.orm.exc import NoResultFound

from pcapi import settings
from pcapi.connectors import googledrive
from pcapi.core import mails
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerer_models
from pcapi.core.users import models as user_models
from pcapi.models import db
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import find_reimbursement_details_by_invoices


logger = logging.getLogger(__name__)


OFFERER_INFORMATION = {
    settings.CGR_EMAIL: {"parent_folder_id": settings.CGR_GOOGLE_DRIVE_CSV_REIMBURSEMENT_ID, "offerer_name": "CGR"},
    settings.KINEPOLIS_EMAIL: {
        "parent_folder_id": settings.KINEPOLIS_GOOGLE_DRIVE_CSV_REIMBURSEMENT_ID,
        "offerer_name": "KINEPOLIS",
    },
}


def _get_csv_reimbursement_email_data(link_to_csv: str) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.PROVIDER_REIMBURSEMENT_CSV.value, params={"LINK_TO_CSV": link_to_csv}
    )


def _get_all_invoices(user_id: int, batch_id: int) -> list:
    invoices = (
        db.session.query(finance_models.Invoice)
        .join(finance_models.Invoice.bankAccount)
        .join(finance_models.BankAccount.offerer)
        .join(offerer_models.UserOfferer, offerer_models.UserOfferer.offererId == offerer_models.Offerer.id)
        .filter(
            offerer_models.Offerer.isActive.is_(True),
            offerer_models.UserOfferer.userId == user_id,
            offerer_models.UserOfferer.isValidated,
            finance_models.BankAccount.isActive.is_(True),
        )
        .join(finance_models.Invoice.cashflows)
        .filter(finance_models.Cashflow.batchId == batch_id)
    ).all()
    return invoices


def _get_filename(offerer_name: str, batch_label: str) -> str:
    return f"{batch_label}_{offerer_name}_remboursements.csv"


def _create_and_get_csv_file(user_id: int, batch_id: int, parent_folder_id: str, filename: str) -> str | None:
    invoices = _get_all_invoices(user_id, batch_id)
    gdrive_api = googledrive.get_backend()

    if len(invoices) == 0:
        logger.info("Zero invoice for user", extra={"user_id": user_id})
        return None
    try:
        file_already_exists_for_this_batch = gdrive_api.search_file(parent_folder_id, filename)
    except ValueError:
        logger.exception(
            "Multiple reimbursement csv files",
            extra={"user_id": user_id, "batch_id": batch_id, "filename": filename},
        )
        return None
    if file_already_exists_for_this_batch:
        logger.info(
            "Reimbursement csv file already exists for this batch and user",
            extra={"user_id": user_id, "batch_id": batch_id, "filename": filename},
        )
        return None

    headers = ReimbursementDetails.get_csv_headers()
    local_path = pathlib.Path(tempfile.mkdtemp()) / filename
    with open(local_path, "a+", encoding="utf-8") as fp:
        writer = csv.writer(fp, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(headers)
        for invoice in invoices:
            reimbursement_details = find_reimbursement_details_by_invoices([invoice.reference])
            for reimbursement_detail in reimbursement_details:
                writer.writerow(reimbursement_detail.as_csv_row())

    try:
        link_to_csv = gdrive_api.create_file(
            parent_folder_id, local_path.name, local_path, response_field="webContentLink"
        )
    except Exception as exc:
        logger.exception("Could not upload csv file to Google Drive", extra={"exc": str(exc)})
        raise exc
    logger.info("Csv file has been uploaded to Google Drive", extra={"link_to_csv": str(link_to_csv)})
    return link_to_csv


def export_csv_and_send_notification_emails(batch_id: int, batch_label: str) -> None:
    for email, infos in OFFERER_INFORMATION.items():
        try:
            user = db.session.query(user_models.User).filter_by(email=email).one()
        except NoResultFound:
            logger.exception("Email is not linked to any user", extra={"email": email})
        filename = _get_filename(infos["offerer_name"], batch_label)
        link_to_csv = _create_and_get_csv_file(user.id, batch_id, infos["parent_folder_id"], filename)
        if link_to_csv is not None:
            data = _get_csv_reimbursement_email_data(link_to_csv)
            mails.send(recipients=[user.email], data=data)
