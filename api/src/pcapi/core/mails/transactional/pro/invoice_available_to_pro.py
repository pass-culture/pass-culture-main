import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sqla_orm

from pcapi.core import mails
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.models as offerers_models
import pcapi.utils.db as db_utils


def send_invoice_available_to_pro_email(invoice: finance_models.Invoice, batch: finance_models.CashflowBatch) -> None:
    period_start, period_end = finance_api.get_invoice_period(batch.cutoff)
    invoice_timespan = db_utils.make_timerange(
        start=datetime.datetime.combine(period_start, datetime.datetime.min.time()),
        end=datetime.datetime.combine(period_end, datetime.datetime.min.time()),
    )
    if period_start == period_end:
        # Usually cashflows and invoices are generated every two weeks. However, in practice nothing
        # forbid to set a cutoff at every date. In this case, if the cashflows and the invoices where
        # generated on the same day, a 16th of the month, this could lead to have a lower and an upper
        # bound strictly equals due to the behavior of `get_invoice_period`, therefor we would have no interval to match on.
        invoice_timespan = db_utils.make_timerange(
            start=datetime.datetime.combine(period_start, datetime.datetime.min.time()), end=batch.cutoff
        )

    data = models.TransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "MONTANT_REMBOURSEMENT": -float(finance_utils.to_euros(invoice.amount)),
            "PERIODE_DEBUT": period_start.strftime("%d-%m-%Y"),
            "PERIODE_FIN": period_end.strftime("%d-%m-%Y"),
        },
    )
    bank_account = (
        finance_models.BankAccount.query.filter(finance_models.BankAccount.id == invoice.bankAccountId)
        .join(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                offerers_models.VenueBankAccountLink.timespan.overlaps(invoice_timespan),
            ),
        )
        .join(offerers_models.Venue, offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId)
        .options(
            sqla_orm.contains_eager(finance_models.BankAccount.venueLinks)
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
