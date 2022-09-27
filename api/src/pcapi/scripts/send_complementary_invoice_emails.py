import logging

import click

from pcapi import settings
from pcapi.core import mails
import pcapi.core.mails.models as mails_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


# FIXME (dbaty, 2022-09-26): remove this command once emails have been sent
@blueprint.cli.command("send_complementary_invoice_emails")
@click.option("--only-rpoint-id", help="Limit to this specific reimbursement point id", default=0)
@click.option("--except-rpoint-id", help="Do not send to this specific reimbursement point id", default=0)
@click.option("--from-file-list", help="Send only to the reimbursement point ids listed in the given file", default="")
def send_emails(only_rpoint_id: int, except_rpoint_id: int, from_file_list: str) -> None:
    """Send an e-mail to each reimbursement point that has a complementary
    invoice.
    """
    query = """
    select
        invoice."reimbursementPointId" as rpoint_id,
        coalesce(venue_contact.email, venue."bookingEmail") as email,
        invoice.reference as reference,
        to_char(invoice.date::date, 'DDMMYYYY') as date,
        invoice.token as token,
        cashflow_batch.label as cashflow_batch_label
    from invoice
    join invoice_cashflow on invoice_cashflow."invoiceId" = invoice.id
    join cashflow ON cashflow.id = invoice_cashflow."cashflowId"
    join cashflow_batch ON cashflow_batch.id = cashflow."batchId"
    join venue on venue.id = invoice."reimbursementPointId"
    left outer join venue_contact on venue_contact."venueId" = venue.id
    where
      reference like '%.2'
    order by cashflow_batch.label
    """
    res = db.session.execute(query)
    rows = res.fetchall()
    by_rpoint = {}
    missing_emails = set()
    for row in rows:
        if not row.email:
            missing_emails.add(row.rpoint_id)
            continue
        if row.rpoint_id not in by_rpoint:
            by_rpoint[row.rpoint_id] = {"email": row.email, "links": []}
        by_rpoint[row.rpoint_id]["links"].append(
            _get_link(row.cashflow_batch_label, row.reference, row.date, row.token)
        )

    if missing_emails:
        print(f"WARN: could not find e-mail address for venue ids: {missing_emails}")

    only_rpoint_ids = None
    if from_file_list:
        with open(from_file_list, "r", encoding="utf-8") as fp:
            only_rpoint_ids = sorted(int(l.strip()) for l in fp.readlines())

    for rpoint_id, info in by_rpoint.items():
        if only_rpoint_id and rpoint_id != only_rpoint_id:
            continue
        if except_rpoint_id and except_rpoint_id == only_rpoint_id:
            continue
        if from_file_list and rpoint_id not in only_rpoint_ids:  # type: ignore [operator]
            continue
        recipient = info["email"]
        links = ", ".join(info["links"])
        links += "."
        _send_email(recipient, links)
        print(f"Sent e-mail to reimbursement point id {rpoint_id}")


def _get_link(cashflow_batch_label: str, reference: str, date: str, token: str) -> str:
    url = f"{settings.OBJECT_STORAGE_URL}/invoices/{token}/{date}-{reference}-Justificatif-de-remboursement-pass-Culture.pdf"
    return f'<a href="{url}">{cashflow_batch_label}</a>'


def _send_email(recipient: str, links: str) -> bool:
    data = mails_models.TransactionalEmailData(
        template=TransactionalEmail.COMPLEMENTARY_INVOICES.value,
        params={"PDF_LINKS": links},
    )
    return mails.send(recipients=[recipient], data=data)
