import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core import mails
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
import pcapi.core.offerers.models as offerers_models
from pcapi.utils.date import get_date_formatted_for_email


def send_invoice_available_to_pro_email(invoice: finance_models.Invoice, batch: finance_models.CashflowBatch) -> None:
    period_start, period_end = finance_api.get_invoice_period(batch.cutoff)
    amount = -float(finance_utils.cents_to_full_unit(invoice.amount))

    data = models.TransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "MONTANT_REMBOURSEMENT": amount,
            "FORMATTED_MONTANT_REMBOURSEMENT": format_price(
                amount, invoice.bankAccount.offerer if invoice.bankAccount else None
            ),
            "PERIODE_DEBUT": get_date_formatted_for_email(period_start),
            "PERIODE_FIN": get_date_formatted_for_email(period_end),
        },
    )
    bank_account = (
        finance_models.BankAccount.query.filter(finance_models.BankAccount.id == invoice.bankAccountId)
        .join(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                offerers_models.VenueBankAccountLink.timespan.contains(batch.cutoff),
            ),
        )
        .join(offerers_models.Venue, offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId)
        .options(
            sa_orm.contains_eager(finance_models.BankAccount.venueLinks)
            .contains_eager(offerers_models.VenueBankAccountLink.venue)
            .load_only(offerers_models.Venue.bookingEmail)
        )
        .one()
    )
    recipients = {
        venue_link.venue.bookingEmail for venue_link in bank_account.venueLinks if venue_link.venue.bookingEmail
    }
    if not recipients:
        return
    mails.send(recipients=recipients, data=data)
