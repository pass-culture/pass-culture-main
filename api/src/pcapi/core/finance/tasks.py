import logging

import sqlalchemy as sa
from pydantic import BaseModel as BaseModelV2

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.finance import api as finance_api
from pcapi.core.internal_notifications.transactional import notify_settlements_executed
from pcapi.models import db

from . import models as finance_models


logger = logging.getLogger(__name__)


class ValidateSettlementBatchRequest(BaseModelV2):
    batch_id: int


@celery_async_task(
    name="tasks.finance.default.validate_settlement_batch",
    model=ValidateSettlementBatchRequest,
)
def settlement_batch_validation_task(payload: ValidateSettlementBatchRequest) -> None:
    settlement_batch = db.session.query(finance_models.SettlementBatch).filter_by(id=payload.batch_id).one()

    if settlement_batch.dateValidated is None:
        logger.error("SettlementBatch is not validated", extra={"batch_id": payload.batch_id})
        return

    settlement_filter = sa.and_(
        finance_models.Settlement.batchId == payload.batch_id,
        finance_models.Settlement.status == finance_models.SettlementStatus.ISSUED,
    )

    invoice_ids = db.session.scalars(
        sa.select(finance_models.InvoiceSettlement.invoiceId)
        .join(finance_models.Settlement, finance_models.InvoiceSettlement.settlementId == finance_models.Settlement.id)
        .where(settlement_filter)
    ).all()

    db.session.query(finance_models.Settlement).filter(settlement_filter).update(
        {"status": finance_models.SettlementStatus.EXECUTED}, synchronize_session=False
    )

    finance_api.validate_invoices(list(invoice_ids))

    db.session.flush()

    # TODO (prouzet, 2026-06-15) Send a mail to pro -- when template is ready

    notify_settlements_executed.send(settlement_batch)
