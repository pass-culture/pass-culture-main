import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.utils.date as date_utils
from pcapi.core import mails
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def get_settlement_validated_email_data(
    *,
    batch_displayed_name: str,
    settlement_amount: int,
    invoice_references: list[str],
    offerer: offerers_models.Offerer,
) -> models.TransactionalEmailData:
    amount = -finance_utils.cents_to_full_unit(settlement_amount)
    return models.TransactionalEmailData(
        template=TransactionalEmail.SETTLEMENT_VALIDATED.value,
        params={
            "FORMATTED_MONTANT_REMBOURSEMENT": format_price(amount, offerer),
            "LIBELLE_VIREMENT": batch_displayed_name,
            "REFERENCES_FACTURES": ", ".join(sorted(invoice_references)),
        },
    )


def send_all_settlement_validated_emails_to_pro(settlement_batch: finance_models.SettlementBatch) -> None:
    batch_displayed_name = settlement_batch.get_displayed_name()

    # Minimal single query to get data for all emails at once without creating too many objects in the ORM.
    # Because we usually have thousands of settlements in a batch, this should avoid OOMkill.
    settlement_rows = (
        db.session.query(
            sa.func.array_agg(offerers_models.Venue.bookingEmail.distinct()).label("recipients"),
            sa.func.array_agg(finance_models.Invoice.reference.distinct()).label("invoice_references"),
            finance_models.Settlement.amount,
            offerers_models.Offerer,
        )
        .select_from(finance_models.Settlement)
        .filter(finance_models.Settlement.batchId == settlement_batch.id)
        .join(finance_models.Settlement.bankAccount)
        .join(finance_models.BankAccount.offerer)
        .options(sa_orm.load_only(offerers_models.Offerer.siren))
        .join(  # inner join because no venue or no bookingEmail means no email to send
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                offerers_models.VenueBankAccountLink.timespan.contains(date_utils.get_naive_utc_now()),
            ),
        )
        .join(offerers_models.VenueBankAccountLink.venue)
        .filter(
            offerers_models.Venue.isSoftDeleted.is_(False),
            offerers_models.Venue.bookingEmail.is_not(None),
        )
        .join(finance_models.Settlement.invoices)
        .group_by(finance_models.Settlement.amount, offerers_models.Offerer.id)
    )

    for row in settlement_rows:
        recipients, invoice_references, amount, offerer = row
        data = get_settlement_validated_email_data(
            batch_displayed_name=batch_displayed_name,
            settlement_amount=amount,
            invoice_references=invoice_references,
            offerer=offerer,
        )
        mails.send(recipients=sorted(recipients), data=data)
