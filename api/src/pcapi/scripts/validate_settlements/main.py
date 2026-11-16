"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=prd \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-44535-validate-settlements \
  -f NAMESPACE=validate_settlements \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

import pcapi.core.finance.models as finance_models
from pcapi.core.finance import api as finance_api
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@atomic()
def main(batch_id: int) -> None:
    logger.info("Validate settlement batch", extra={"batch_id": batch_id})

    settlement_batch = db.session.query(finance_models.SettlementBatch).filter_by(id=batch_id).one()

    if settlement_batch.dateValidated is None:
        logger.error("SettlementBatch is not validated", extra={"batch_id": batch_id})
        return

    settlement_filter = sa.and_(
        finance_models.Settlement.batchId == batch_id,
        finance_models.Settlement.status == finance_models.SettlementStatus.ISSUED,
    )

    invoice_ids = db.session.scalars(
        sa.select(finance_models.InvoiceSettlement.invoiceId)
        .join(finance_models.Settlement, finance_models.InvoiceSettlement.settlementId == finance_models.Settlement.id)
        .where(settlement_filter)
    ).all()

    count_updated = (
        db.session.query(finance_models.Settlement)
        .filter(settlement_filter)
        .update({"status": finance_models.SettlementStatus.EXECUTED}, synchronize_session=False)
    )
    logger.info("%d settlements marked as as EXECUTED", count_updated)

    db.session.flush()

    logger.info("Invoice IDs", extra={"batch_id": batch_id, "invoice_ids": invoice_ids})
    finance_api.validate_invoices(list(invoice_ids))

    db.session.flush()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", type=int, required=True)
    args = parser.parse_args()

    main(args.batch_id)

    logger.info("Finished")
