from pcapi.core import mails
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.utils.date import get_date_formatted_for_email


def get_settlement_rejected_email_data(settlement: finance_models.Settlement) -> models.TransactionalEmailData:
    date_validated = settlement.batch.dateValidated
    assert date_validated  # we can't have a rejected settlement without a validated batch
    return models.TransactionalEmailData(
        template=TransactionalEmail.SETTLEMENT_REJECTED.value,
        params={
            "DATE_VIREMENT": get_date_formatted_for_email(date_validated),
        },
    )


def send_settlement_rejected_email_to_pro(settlement: finance_models.Settlement) -> None:
    recipients = [
        link.venue.bookingEmail
        for link in settlement.bankAccount.venueLinks
        if link.timespan.upper is None and link.venue.bookingEmail is not None
    ]
    if not recipients:
        return

    data = get_settlement_rejected_email_data(settlement)
    mails.send(recipients=recipients, data=data)
