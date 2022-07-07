from pcapi.core import mails
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import repository as offerers_repository


def send_invoice_available_to_pro_email(invoice: finance_models.Invoice, use_reimbursement_point: bool) -> bool:
    data = SendinblueTransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "MONTANT_REMBOURSEMENT": -finance_utils.to_euros(invoice.amount),  # type: ignore [arg-type]
        },
    )
    if use_reimbursement_point:
        recipient = invoice.reimbursementPoint.bookingEmail
        if not recipient:
            return False
    else:
        venue = offerers_repository.find_venue_by_siret(invoice.businessUnit.siret)  # type: ignore[arg-type]
        if not venue or not venue.bookingEmail:
            return False
        recipient = venue.bookingEmail
    return mails.send(recipients=[recipient], data=data)
