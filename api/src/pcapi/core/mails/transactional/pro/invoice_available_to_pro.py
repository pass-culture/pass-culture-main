import calendar
from datetime import date
from datetime import timedelta
from typing import Union

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import repository as offerers_repository


def get_invoice_available_to_pro_email_data(invoice) -> Union[dict, SendinblueTransactionalEmailData]:
    start_date, end_date = get_invoice_date_range(invoice)
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "montant": invoice.amount,
            "date_min": start_date.strftime("%d/%m/%Y"),
            "date_max": end_date.strftime("%d/%m/%Y"),
        },
    )


def get_invoice_date_range(invoice) -> tuple[str, str]:
    # We generate invoices few days after the payment script.
    # An invoice genereted after the 15th of a month covers the first half of this
    # month while an invoice generated before the 15th of a months covers the last
    # two weeks of the previous month.
    invoice_date = invoice.date
    if invoice_date.day > 15:
        start_date = date(invoice_date.year, invoice_date.month, 1)
        end_date = date(invoice_date.year, invoice_date.month, 15)
    else:
        previous_month = invoice_date - timedelta(days=30)
        last_day_of_month = calendar.monthrange(previous_month.year, previous_month.month)[1]
        start_date = date(previous_month.year, previous_month.month, 15)
        end_date = date(previous_month.year, previous_month.month, last_day_of_month)
    return start_date, end_date


def send_invoice_available_to_pro_email(invoice) -> bool:
    data = get_invoice_available_to_pro_email_data(invoice)
    recipient = offerers_repository.find_venue_by_siret(invoice.businessUnit.siret).bookingEmail
    return mails.send(recipients=[recipient], data=data)
