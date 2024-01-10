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
from pcapi.models.feature import FeatureToggle


def send_invoice_available_to_pro_email(invoice: finance_models.Invoice, batch: finance_models.CashflowBatch) -> None:
    period_start, period_end = finance_api.get_invoice_period(batch.cutoff)
    data = models.TransactionalEmailData(
        template=TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value,
        params={
            "MONTANT_REMBOURSEMENT": -float(finance_utils.to_euros(invoice.amount)),
            "PERIODE_DEBUT": period_start.strftime("%d-%m-%Y"),
            "PERIODE_FIN": period_end.strftime("%d-%m-%Y"),
        },
    )
    if FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY.is_active():
        bank_account = (
            finance_models.BankAccount.query.filter(finance_models.BankAccount.id == invoice.bankAccountId)
            .join(
                offerers_models.VenueBankAccountLink,
                sa.and_(
                    offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
                ),
            )
            .join(offerers_models.Venue, offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId)
            .options(
                sqla_orm.joinedload(finance_models.BankAccount.venueLinks)
                .joinedload(offerers_models.VenueBankAccountLink.venue)
                .load_only(offerers_models.Venue.bookingEmail)
            )
            .one()
        )
        recipients = [
            venue_link.venue.bookingEmail for venue_link in bank_account.venueLinks if venue_link.venue.bookingEmail
        ]
        if not recipients:
            return
    else:
        if not invoice.reimbursementPoint.bookingEmail:
            return
        recipients = [invoice.reimbursementPoint.bookingEmail]
    mails.send(recipients=recipients, data=data)
