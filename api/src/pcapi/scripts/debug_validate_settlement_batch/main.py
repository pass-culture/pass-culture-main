"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=prd \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bsr-debug-settlement_batch_validation_task \
  -f NAMESPACE=debug_validate_settlement_batch \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from functools import partial

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.utils.date as date_utils
from pcapi.core import mails
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)


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

    for i, row in enumerate(settlement_rows):
        recipients, invoice_references, amount, offerer = row
        logger.info("Debug - row %i", i, extra={"invoice_references": invoice_references})
        data = get_settlement_validated_email_data(
            batch_displayed_name=batch_displayed_name,
            settlement_amount=amount,
            invoice_references=invoice_references,
            offerer=offerer,
        )
        mails.send(recipients=sorted(recipients), data=data)


def main(batch_id: int) -> None:
    logger.info("Debug validate settlement batch - start")

    with atomic():
        settlement_batch = db.session.query(finance_models.SettlementBatch).filter_by(id=batch_id).one()

        if settlement_batch.dateValidated is None:
            logger.error("SettlementBatch is not validated", extra={"batch_id": batch_id})
            return

        logger.info(
            "Debug validate settlement batch - SettlementBatch fetched",
            extra={"batch_id": settlement_batch.id, "label": settlement_batch.label},
        )

        settlement_filter = sa.and_(
            finance_models.Settlement.batchId == batch_id,
            finance_models.Settlement.status == finance_models.SettlementStatus.ISSUED,
        )

        invoice_ids = db.session.scalars(
            sa.select(finance_models.InvoiceSettlement.invoiceId)
            .join(
                finance_models.Settlement, finance_models.InvoiceSettlement.settlementId == finance_models.Settlement.id
            )
            .where(settlement_filter)
        ).all()

        logger.info("Debug validate settlement batch - invoice_ids fetched", extra={"count": len(invoice_ids)})

        updated = (
            db.session.query(finance_models.Settlement)
            .filter(settlement_filter)
            .update({"status": finance_models.SettlementStatus.EXECUTED}, synchronize_session=False)
        )

        logger.info("Debug validate settlement batch - Settlements EXECUTED", extra={"updated": updated})

        invoice_ids_list = list(invoice_ids)
        finance_api.validate_invoices(invoice_ids_list)

        logger.info("Debug validate settlement batch - validate_invoices returned")

        db.session.flush()

    logger.info("Debug validate settlement batch - calling send_all_settlement_validated_emails_to_pro")

    send_all_settlement_validated_emails_to_pro(settlement_batch)

    logger.info("Debug validate settlement batch - send_all_settlement_validated_emails_to_pro returned")

    on_commit(partial(logger.info, "Debug - last on_commit"))


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", type=int, required=True)
    args = parser.parse_args()

    main(args.batch_id)

    logger.info("Finished")
