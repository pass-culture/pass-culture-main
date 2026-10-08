from pcapi.core import mails
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.utils import date as date_utils


def get_refund_settlement_received_data(settlement: finance_models.Settlement) -> models.TransactionalEmailData:
    [invoice] = settlement.invoices  # by definition, there's only one invoice for refund settlements
    return models.TransactionalEmailData(
        template=TransactionalEmail.REFUND_SETTLEMENT_RECEIVED.value,
        params={
            "FORMATTED_MONTANT_REMBOURSEMENT": format_price(
                finance_utils.cents_to_full_unit(settlement.amount), settlement.bankAccount.offerer
            ),
            "SETTLEMENT_DATE": date_utils.get_date_formatted_for_email(settlement.settlementDate),
            "REFERENCE": invoice.reference,
        },
    )


def send_refund_settlement_received(settlement: finance_models.Settlement) -> None:
    recipients = [
        link.venue.bookingEmail
        for link in settlement.bankAccount.venueLinks
        if link.timespan.upper is None and link.venue.bookingEmail is not None
    ]
    if not recipients:
        return

    data = get_refund_settlement_received_data(settlement)
    mails.send(recipients=recipients, data=data)
