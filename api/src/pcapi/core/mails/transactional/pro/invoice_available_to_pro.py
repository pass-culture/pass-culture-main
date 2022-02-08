from typing import Union

from pcapi.core import mails
import pcapi.core.finance.utils as finance_utils
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import repository as offerers_repository


def get_invoice_available_to_pro_email_data(invoice) -> Union[dict, SendinblueTransactionalEmailData]:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "montant": -finance_utils.to_euros(invoice.amount),
        },
    )


def send_invoice_available_to_pro_email(invoice) -> bool:
    data = get_invoice_available_to_pro_email_data(invoice)
    recipient = offerers_repository.find_venue_by_siret(invoice.businessUnit.siret).bookingEmail
    if not recipient:
        return False
    return mails.send(recipients=[recipient], data=data)
