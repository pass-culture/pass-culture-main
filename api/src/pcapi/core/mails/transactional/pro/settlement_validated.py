from pcapi.core import mails
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price


def get_settlement_validated_email_data(settlement: finance_models.Settlement) -> models.TransactionalEmailData:
    amount = finance_utils.cents_to_full_unit(settlement.amount)
    return models.TransactionalEmailData(
        template=TransactionalEmail.SETTLEMENT_VALIDATED.value,
        params={
            "FORMATTED_MONTANT_REMBOURSEMENT": format_price(amount, settlement.bankAccount.offerer),
            "LIBELLE_VIREMENT": settlement.batch.get_displayed_name(),
            "REFERENCES_FACTURES": ", ".join(sorted([invoice.reference for invoice in settlement.invoices])),
        },
    )


def send_settlement_validated_email_to_pro(settlement: finance_models.Settlement) -> None:
    recipients = [
        link.venue.bookingEmail
        for link in settlement.bankAccount.venueLinks
        if link.timespan.upper is None and link.venue.bookingEmail is not None
    ]
    if not recipients:
        return

    data = get_settlement_validated_email_data(settlement)
    mails.send(recipients=recipients, data=data)
