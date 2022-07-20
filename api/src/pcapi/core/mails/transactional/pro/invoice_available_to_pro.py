from pcapi.core import mails
import pcapi.core.finance.utils as finance_utils
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import repository as offerers_repository


def send_invoice_available_to_pro_email(invoice) -> bool:  # type: ignore [no-untyped-def]
    data = SendinblueTransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "MONTANT_REMBOURSEMENT": -finance_utils.to_euros(invoice.amount),
        },
    )
    venue = offerers_repository.find_venue_by_siret(invoice.businessUnit.siret)
    if not venue or not venue.bookingEmail:
        return False
    recipient = venue.bookingEmail
    return mails.send(recipients=[recipient], data=data)
