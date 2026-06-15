import logging

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_settlements() -> None:
    logger.info("create_industrial_settlements")

    cashflow_batches = (
        db.session.query(finance_models.CashflowBatch).order_by(finance_models.CashflowBatch.cutoff).all()
    )

    for i, cashflow_batch in enumerate(cashflow_batches):
        settlement_batch = finance_factories.SettlementBatchFactory(
            name=cashflow_batch.label,
            label=f"{cashflow_batch.label} - cutoff du {cashflow_batch.cutoff.strftime('%d/%m/%Y à %Hh%M')}",
            dateValidated=date_utils.get_naive_utc_now() if i < 5 else None,
        )
        for cashflow in cashflow_batch.cashflows:
            for invoice in cashflow.invoices:
                finance_factories.SettlementFactory(
                    bankAccount=invoice.bankAccount, amount=invoice.amount, batch=settlement_batch
                )

    logger.info("Created %s settlements", db.session.query(finance_models.Settlement).count())
