import logging

import sqlalchemy as sa
from pydantic import BaseModel as BaseModelV2

import pcapi.core.mails.transactional as transactional_mails
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.finance import api as finance_api
from pcapi.core.internal_notifications.transactional import notify_settlements_executed
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic

from . import models as finance_models


logger = logging.getLogger(__name__)


class ValidateSettlementBatchRequest(BaseModelV2):
    batch_id: int


@celery_async_task(
    name="tasks.finance.default.validate_settlement_batch",
    model=ValidateSettlementBatchRequest,
)
def settlement_batch_validation_task(payload: ValidateSettlementBatchRequest) -> None:
    extra = {"batch_id": payload.batch_id}
    logger.info("validate_settlement_batch - starting task", extra=extra)

    with atomic():
        settlement_batch = db.session.query(finance_models.SettlementBatch).filter_by(id=payload.batch_id).one()

        if settlement_batch.dateValidated is None:
            logger.error("SettlementBatch is not validated", extra=extra)
            return

        settlement_filter = sa.and_(
            finance_models.Settlement.batchId == payload.batch_id,
            finance_models.Settlement.status == finance_models.SettlementStatus.ISSUED,
        )

        invoice_ids = db.session.scalars(
            sa.select(finance_models.InvoiceSettlement.invoiceId)
            .join(
                finance_models.Settlement, finance_models.InvoiceSettlement.settlementId == finance_models.Settlement.id
            )
            .where(settlement_filter)
        ).all()

        db.session.query(finance_models.Settlement).filter(settlement_filter).update(
            {"status": finance_models.SettlementStatus.EXECUTED}, synchronize_session=False
        )

        invoice_ids_list = list(invoice_ids)

        logger.info("validate_settlement_batch - validate invoices", extra=extra | {"count": len(invoice_ids_list)})
        finance_api.validate_invoices(invoice_ids_list)

        db.session.flush()

    logger.info("validate_settlement_batch - objects updated in database, now preparing emails", extra=extra)

    # Enqueue a lot of emails outside managed transaction to avoid OOMkill
    transactional_mails.send_all_settlement_validated_emails_to_pro(settlement_batch)

    notify_settlements_executed.send(settlement_batch, len(invoice_ids_list))

    logger.info("validate_settlement_batch - finished", extra=extra)
