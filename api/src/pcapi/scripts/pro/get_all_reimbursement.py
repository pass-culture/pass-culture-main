import csv
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
import pathlib
import tempfile

import sqlalchemy as sqla

from pcapi import settings
from pcapi.connectors import googledrive
from pcapi.core import mails
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerer_models
from pcapi.core.users import models as user_models
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import find_reimbursement_details_by_invoices


logger = logging.getLogger(__name__)


PERIOD_IN_DAYS = 15
OFFERER_INFORMATIONS = {
    settings.CGR_EMAIL: {"parent_folder_id": settings.CGR_GOOGLE_DRIVE_CSV_REIMBURSEMENT_ID, "structure_name": "CGR"},
    settings.KINEPOLIS_EMAIL: {
        "parent_folder_id": settings.KINEPOLIS_GOOGLE_DRIVE_CSV_REIMBURSEMENT_ID,
        "structure_name": "KINEPOLIS",
    },
}


def _get_csv_reimbursement_email_data(link_to_csv: str) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.CSV_REIMBURSEMENT.value, params={"link_to_csv": link_to_csv}
    )


def _get_all_invoices(user_id: int) -> list:
    invoices = (
        finance_models.Invoice.query.join(finance_models.Invoice.bankAccount)
        .join(finance_models.BankAccount.offerer)
        .join(offerer_models.UserOfferer, offerer_models.UserOfferer.offererId == offerer_models.Offerer.id)
        .filter(
            offerer_models.Offerer.isActive.is_(True),
            offerer_models.UserOfferer.userId == user_id,
            sqla.not_(offerer_models.UserOfferer.isRejected) & sqla.not_(offerer_models.UserOfferer.isDeleted),
            offerer_models.UserOfferer.isValidated,
            finance_models.BankAccount.isActive.is_(True),
            finance_models.Invoice.date > datetime.utcnow() - timedelta(days=PERIOD_IN_DAYS),
        )
        .order_by(finance_models.Invoice.date.desc())
    ).all()
    return invoices


def _get_filename(structure_name: str) -> str:
    period_start = (date.today() - timedelta(days=PERIOD_IN_DAYS)).strftime("%Y%m%d")
    period_end = date.today().strftime("%Y%m%d")
    return f"{period_start}_{period_end}_{structure_name}_remboursements.csv"


def _create_and_get_csv_file(user_id: int, parent_folder_id: str, filename: str) -> str | None:
    invoices = _get_all_invoices(user_id)

    if len(invoices) == 0:
        logger.info("Zero invoice for user", extra={"user_id": user_id})
        return None

    reimbursement_details = find_reimbursement_details_by_invoices([invoice.reference for invoice in invoices])
    csv_lines = [reimbursement_detail.as_csv_row() for reimbursement_detail in reimbursement_details]
    headers = ReimbursementDetails.get_csv_headers()
    local_path = pathlib.Path(tempfile.mkdtemp()) / filename
    with open(local_path, "w+", encoding="utf-8") as fp:
        writer = csv.writer(fp, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(headers)
        writer.writerows(csv_lines)

    gdrive_api = googledrive.get_backend()

    try:
        link_to_csv = gdrive_api.create_file(
            parent_folder_id, local_path.name, local_path, response_field="webContentLink"
        )
    except Exception as exc:
        logger.exception("Could not upload csv file to Google Drive", extra={"exc": str(exc)})
        raise exc
    logger.info("Csv file has been uploaded to Google Drive", extra={"link_to_csv": str(link_to_csv)})
    return link_to_csv


def export_csv_and_send_notfication_emails() -> None:
    for email, infos in OFFERER_INFORMATIONS.items():
        user = user_models.User.query.filter_by(email=email).one_or_none()
        if user is None:
            logger.error("Email is not linked to any user", extra={"email": email})
            continue
        filename = _get_filename(infos["structure_name"])
        link_to_csv = _create_and_get_csv_file(user.id, infos["parent_folder_id"], filename)
        if link_to_csv is not None:
            data = _get_csv_reimbursement_email_data(link_to_csv)
            mails.send(recipients=[user.email], data=data)
