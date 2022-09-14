from pcapi.core import mails
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_invoice_available_to_pro_email(invoice: finance_models.Invoice) -> bool:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "MONTANT_REMBOURSEMENT": -finance_utils.to_euros(invoice.amount),
        },
    )
    recipient = invoice.reimbursementPoint.bookingEmail
    if not recipient:
        return False
    return mails.send(recipients=[recipient], data=data)
